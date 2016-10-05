from __future__ import division
import math
from collections import defaultdict, Counter
import cPickle
import zlib
try:  
    import pymel.core as pm
except ImportError:
    pm = None

def most_common_element(x):
    data = Counter(x)
    return data.most_common(1)[0][0]


class Voxelise(object):
    
    _order = [(-1, -1, -1), (-1, -1, 1), (-1, 1, -1), (-1, 1, 1), (1, -1, -1), (1, -1, 1), (1, 1, -1), (1, 1, 1)]
    _default_empty = 0
    _default_id = 1
    
    def __init__(self, chunk_size, voxel_size=0):
        
        if chunk_size < 1:
            self._errors(1)
        if voxel_size < 0:
            self._errors(2)
        if voxel_size > chunk_size:
            voxel_size = chunk_size
        self._chunk_size = chunk_size - 1
        self._voxel_size = voxel_size
        
        self.coordinate_max = pow(2, self._chunk_size)
        self.coordinate_min = 1 - self.coordinate_max
        
        print 'Min Coordinate: {}, Max Coordinate: {}, Voxel Size: {}'.format(self.coordinate_min, self.coordinate_max, self._voxel_size)
        
        self.data = defaultdict(self._default_list)
        self._edited = defaultdict(set)
    
    def _default_list(self, id=_default_empty, level=None):
        return [id, level] + [id] * 8
    
    def _errors(self, t=None):
        if t is None:
            return
        elif t == 1:
            raise ValueError('chunk size must be 1 or above')
        elif t == 2:
             raise ValueError('voxel size must be 0 or above')
    
    def find_path(self, value, voxel_size=None):
        """Find path of a voxel."""
        
        if voxel_size is None:
            voxel_size = self._voxel_size
        if voxel_size < 0:
            self._errors(2)
        
        value *= 2
        value += 1
        if value >= 0:
            chunk = int(math.ceil(value / self.coordinate_max)) - 1
            value -= chunk * self.coordinate_max
        else:
            chunk = int(math.ceil(value / self.coordinate_max))
            value -= chunk * self.coordinate_max
        
        path = []
        current_level = self._chunk_size + 1
        while current_level > voxel_size:
            current_level -= 1
            multiplier = 1 if value >= 0 else -1
            path.append(multiplier)
            value -= pow(2, current_level) * multiplier
        
        return chunk, path

    def add_points(self, points, id=None, voxel_size=None):
        
        if isinstance(points, dict):
            for point, original_id in points.iteritems():
                self.add_point(point, id=id if id is not None else original_id, voxel_size=voxel_size, recalculate=False)
                #print point, id if id is not None else original_id
        else:
            for point in points:
                self.add_point(point, id=id, voxel_size=voxel_size, recalculate=False)
        self.recalculate_lod()
        
    def add_point(self, coordinate, id=_default_id, voxel_size=None, recalculate=True):
        path_data = [self.find_path(i, voxel_size) for i in coordinate]
        chunk = tuple(i[0] for i in path_data)
        path = tuple(zip(*[i[1] for i in path_data]))
        
        current = self.data[chunk]
        current[1] = self._chunk_size + 1
        count = self._chunk_size
        for coordinate in path[:-1]:
            index = self._order.index(coordinate) + 2
            
            try:
                current[index][1]
            except TypeError:
                current[index] = self._default_list(current[index], count)
                
            current = current[index]
            count -= 1
            
        index = self._order.index(path[-1]) + 2
        current[index] = id
        
        self._edited[chunk].add(path)
        if recalculate:
            self.recalculate_lod()
    
    def recalculate_lod(self):
        temp_set = {k: set(v) for k, v in self._edited.iteritems()}
        while temp_set:
            for chunk in temp_set:
                for path in temp_set[chunk]:
                    
                    #Find current point in list
                    current = self.data[chunk]
                    for j in path[:-1]:
                        index = self._order.index(j) + 2
                        try:
                            current[index][1]
                        except TypeError:
                            current[index] = self._default_list(current[index], current[1] - 1)
                        current = current[index]
                    
                    #Calculate IDs to find the most common
                    all_ids = []
                    recursion_used = False
                    try:
                        for j in current[2:]:
                            try:
                                all_ids.append(j[0])
                            except TypeError:
                                all_ids.append(j)
                            else:
                                recursion_used = True
                    except TypeError:
                        continue
                    current[0] = most_common_element(all_ids)
                    
                    #Merge lists that are all the same
                    if not recursion_used and len(set(all_ids)) == 1:
                        current = self.data[chunk]
                        for j in path[:-2]:
                            current = current[self._order.index(j) + 2]
                        current[self._order.index(path[-2]) + 2] = all_ids[0]
                        
            
            #Trim down set to run on the next level
            invalid_keys = []
            for k, v in temp_set.iteritems():
                new_v = []
                for i in v:
                    shortened = i[:-1]
                    if shortened:
                        new_v.append(shortened)
                if new_v:
                    temp_set[k] = set(new_v)
                else:
                    invalid_keys.append(k)
            for i in invalid_keys:
                del temp_set[i]
        
        self._edited = defaultdict(set)

    def read_points(self, level_of_detail=None):
        self._all_points = []
        
        #if level_of_detail is None:
        #    level_of_detail = self._voxel_size
        
        for chunk in self.data:
            total = [i * self.coordinate_max for i in chunk]
            self._read_recursive(self.data[chunk], total, lod=level_of_detail)
            
        all_points = self._all_points
        del self._all_points
        return all_points

    def _read_recursive(self, current_list, total, level=None, lod=None):
        count = 0
        try:
            if lod is not None and level == lod:
                raise TypeError()
                
            multiplier = pow(2, current_list[1] - 1)
        except TypeError:
            if total:
                try:
                    id = current_list[0]
                except TypeError:
                    id = current_list
                round_amount = pow(2, level)
                self._all_points.append([id, level, tuple(round_amount * int(round((i - 1) / (round_amount * 2))) for i in total)])
                
        else:
            for i in current_list[2:]:
                new_value = [j * multiplier for j in self._order[count]]
                new_total = [a + b for a, b in zip(total, new_value)]
                if i:
                    self._read_recursive(i, new_total, level=current_list[1] - 1, lod=lod)
                count += 1

class MayaVoxel(object):
    """Voxel functions specific to Maya"""
    def __init__(self, vox_object):
        self.vox = vox_object
    
    def draw_cubes(self, lod=None):
        for id, level, location in sorted(self.vox.read_points(lod)):
            
            size = pow(2, level)
            offset = pow(2, level - 1) - 0.5
            #multiplier, movement = move_offsets(level)
            
            cube = pm.polyCube(w=size, h=size, d=size)[0]
            pm.move(cube, [i + offset for i in location])
            
            #Set attribute and UV map
            pm.addAttr(cube, shortName='bid', longName='BlockID', attributeType='byte')
            pm.setAttr('{}.bid'.format(cube), id)
            UVSize = size
            pm.polyEditUV('{}.map[:]'.format(cube), su=UVSize*3, sv=UVSize*4)
