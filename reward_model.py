from dataclasses import dataclass, field
from typing import List, Dict, Optional
from lxml import etree
import re

@dataclass
class RewardItem:
    item_id: int
    count: int

@dataclass
class Requirement:
    type: str
    value: str

@dataclass
class Reward:
    id: int
    name: str
    description: str
    reset_period: str
    reward_items: List[RewardItem]
    requirements: List[Requirement]
    class_filter: List[int]
    min_level: int
    max_level: int
    category: int = 0
    targetloc_scale: Optional[List[float]] = None
    mob_ids: list = field(default_factory=list)

class RewardModel:
    def __init__(self):
        self.rewards: Dict[int, Reward] = {}
    
    def load_from_xml(self, xml_path: str):
        tree = etree.parse(xml_path)
        root = tree.getroot()
        
        for reward_elem in root.findall('.//one_day_reward'):
            reward = self._parse_xml_reward(reward_elem)
            self.rewards[reward.id] = reward
    
    def load_from_text(self, text_path: str):
        with open(text_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into individual rewards
        reward_blocks = re.findall(r'onedayreward_begin(.*?)onedayreward_end', content, re.DOTALL)
        
        for block in reward_blocks:
            text_reward = self._parse_text_reward(block)
            # Only update fields for rewards already loaded from XML
            if text_reward.id in self.rewards:
                reward = self.rewards[text_reward.id]
                reward.name = text_reward.name
                reward.description = text_reward.description
                reward.category = text_reward.category
                # Optionally update reward_id if needed (usually same as id)
                # reward.reward_id = text_reward.reward_id
                self.rewards[text_reward.id] = reward
            # If not in XML, skip (do not add new rewards from text)
    
    def _parse_xml_reward(self, elem) -> Reward:
        reward_id = int(elem.find('id').text)
        name = elem.find('name').text
        description = elem.find('description').text
        reset_period = elem.find('reset_time').text
        
        # Parse reward items
        reward_items = []
        for item_elem in elem.findall('.//reward_item'):
            item_id = int(item_elem.get('id'))
            count = int(item_elem.get('count'))
            reward_items.append(RewardItem(item_id, count))
        
        # Parse requirements
        requirements = []
        req_elem = elem.find('.//requirement')
        if req_elem is not None:
            for child in req_elem:
                req_type = child.tag
                req_value = child.text if child.text else child.get('count', '1')
                requirements.append(Requirement(req_type, req_value))
        
        # Parse conditions
        min_level = 0
        max_level = 99
        class_filter = [-1]  # Default to all classes
        mob_ids = []
        
        cond_elem = elem.find('.//cond')
        if cond_elem is not None:
            player_elem = cond_elem.find('.//player')
            if player_elem is not None:
                min_level = int(player_elem.get('minLevel', 0))
                max_level = int(player_elem.get('maxLevel', 99))
            target_elem = cond_elem.find('.//target')
            if target_elem is not None and target_elem.get('mobId'):
                mob_ids = [int(x) for x in target_elem.get('mobId').split(';') if x.strip()]
        
        return Reward(
            id=reward_id,
            name=name,
            description=description,
            reset_period=reset_period,
            reward_items=reward_items,
            requirements=requirements,
            class_filter=class_filter,
            min_level=min_level,
            max_level=max_level,
            targetloc_scale=None,
            category=0,
            mob_ids=mob_ids
        )
    
    def _parse_text_reward(self, block: str) -> Reward:
        # Extract key-value pairs robustly
        data = {}
        for part in block.split('\t'):
            if '=' in part:
                key, value = part.split('=', 1)
                data[key.strip()] = value.strip()
            # else: skip malformed part
        
        # Parse basic info
        reward_id = int(data['id'])
        name = data['reward_name'].strip('[]')
        description = data['reward_desc'].strip('[]')
        reset_period = data['reset_period']
        
        # Parse reward items using regex for {item_id;count}
        reward_items = []
        items_str = data.get('reward_item', '').strip('{}')
        if items_str:
            for match in re.finditer(r'\{(\d+);(\d+)\}', items_str):
                item_id, count = map(int, match.groups())
                reward_items.append(RewardItem(item_id, count))
        
        # Parse class filter
        class_filter = [-1]
        if 'class_filter' in data:
            class_filter = [int(x) for x in data['class_filter'].strip('{}').split(';') if x.strip()]
        
        # Parse level conditions
        min_level, max_level = 0, 99
        if 'can_condition_level' in data:
            level_range = data['can_condition_level'].strip('{}').split(';')
            if len(level_range) >= 2:
                min_level = int(level_range[0])
                max_level = int(level_range[1])
        
        # Parse requirements (support any tag except known meta fields)
        requirements = []
        meta_fields = {
            'id', 'reward_id', 'reward_name', 'reward_desc', 'reward_period', 'class_filter',
            'reset_period', 'condition_count', 'condition_level', 'can_condition_level',
            'can_condition_day', 'category', 'reward_item', 'targetloc_scale', 'distribution_type',
            'onedayreward_begin', 'onedayreward_end'
        }
        # If condition_count > 0, use kill_mob as before
        if 'condition_count' in data and data['condition_count'].isdigit() and int(data['condition_count']) > 0:
            req_type = 'kill_mob'
            req_value = data['condition_count']
            requirements.append(Requirement(req_type, req_value))
        # Add all other non-meta fields as requirements
        for key in data:
            if key not in meta_fields and data[key] != '':
                requirements.append(Requirement(key, data[key] if data[key] else '1'))
        
        # Parse target location if present
        targetloc = None
        if 'targetloc_scale' in data and data['targetloc_scale'].strip('{}'):
            targetloc = [float(x) for x in data['targetloc_scale'].strip('{}').split(';') if x.strip()]
        
        # Parse category
        category = 0
        if 'category' in data and data['category'].isdigit():
            category = int(data['category'])
        
        mob_ids = []
        if 'mob_ids' in data and data['mob_ids'].strip('{}'):
            mob_ids = [int(x) for x in data['mob_ids'].strip('{}').split(';') if x.strip()]
        
        return Reward(
            id=reward_id,
            name=name,
            description=description,
            reset_period=reset_period,
            reward_items=reward_items,
            requirements=requirements,
            class_filter=class_filter,
            min_level=min_level,
            max_level=max_level,
            targetloc_scale=targetloc,
            category=category,
            mob_ids=mob_ids
        )
    
    def save_to_xml(self, xml_path: str):
        root = etree.Element('one_day_rewards')
        
        for reward in self.rewards.values():
            reward_elem = etree.SubElement(root, 'one_day_reward')
            
            # Basic info
            etree.SubElement(reward_elem, 'id').text = str(reward.id)
            etree.SubElement(reward_elem, 'name').text = reward.name
            etree.SubElement(reward_elem, 'description').text = reward.description
            etree.SubElement(reward_elem, 'reset_time').text = reward.reset_period
            
            # Reward items
            items_elem = etree.SubElement(reward_elem, 'reward_items')
            for item in reward.reward_items:
                item_elem = etree.SubElement(items_elem, 'reward_item')
                item_elem.set('id', str(item.item_id))
                item_elem.set('count', str(item.count))
            
            # Requirements
            if reward.requirements:
                req_elem = etree.SubElement(reward_elem, 'requirement')
                for req in reward.requirements:
                    req_type_elem = etree.SubElement(req_elem, req.type)
                    req_type_elem.text = req.value
            
            # Conditions
            cond_elem = etree.SubElement(reward_elem, 'cond')
            and_elem = etree.SubElement(cond_elem, 'and')
            player_elem = etree.SubElement(and_elem, 'player')
            player_elem.set('minLevel', str(reward.min_level))
            player_elem.set('maxLevel', str(reward.max_level))
            if reward.mob_ids:
                target_elem = etree.SubElement(and_elem, 'target')
                target_elem.set('mobId', ';'.join(map(str, reward.mob_ids)))
        
        tree = etree.ElementTree(root)
        tree.write(xml_path, pretty_print=True, encoding='utf-8')
    
    def save_to_text(self, text_path: str):
        with open(text_path, 'w', encoding='utf-8') as f:
            for reward in self.rewards.values():
                f.write('onedayreward_begin\t')
                
                # Basic info
                f.write(f'id={reward.id}\t')
                f.write(f'reward_id={reward.id}\t')
                f.write(f'reward_name=[{reward.name}]\t')
                f.write(f'reward_desc=[{reward.description}]\t')
                f.write(f'reward_period=[{reward.reset_period}]\t')
                
                # Class filter
                class_filter_str = ';'.join(map(str, reward.class_filter))
                f.write(f'class_filter={{{class_filter_str}}}\t')
                
                # Reset period
                f.write(f'reset_period={self._get_reset_period_number(reward.reset_period)}\t')
                
                # Requirements
                has_kill_mob = False
                for req in reward.requirements:
                    if req.type == 'kill_mob':
                        f.write(f'condition_count={req.value}\t')
                        has_kill_mob = True
                    else:
                        f.write(f'{req.type}={req.value}\t')
                if not has_kill_mob:
                    f.write('condition_count=0\t')
                
                # Level conditions
                f.write(f'condition_level={reward.min_level}\t')
                f.write(f'can_condition_level={{{reward.min_level};{reward.max_level};0}}\t')
                f.write('can_condition_day={}\t')
                
                # Category
                f.write(f'category={reward.category}\t')
                
                # Reward items
                items_str = ';'.join(f'{{{item.item_id};{item.count}}}' for item in reward.reward_items)
                f.write(f'reward_item={{{items_str}}}\t')
                
                # Target location
                if reward.targetloc_scale:
                    loc_str = ';'.join(map(str, reward.targetloc_scale))
                    f.write(f'targetloc_scale={{{loc_str}}}\t')
                else:
                    f.write('targetloc_scale={}\t')
                
                # Mob IDs
                if reward.mob_ids:
                    f.write(f'mob_ids={{{";".join(map(str, reward.mob_ids))}}}\t')
                
                f.write('onedayreward_end\n')
    
    def _get_reset_period_number(self, period: str) -> int:
        period_map = {
            'DAILY': 1,
            'WEEKLY': 2,
            'MONTHLY': 3,
            'SINGLE': 4
        }
        return period_map.get(period, 1) 