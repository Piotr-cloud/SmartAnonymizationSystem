'''
Created on Feb 26, 2023

@author: piotr
'''



class RAM_Info_Cls():
    
    def __init__(self, RAM_start, RAM_max, RAM_last):
        
        self.RAM_start = RAM_start
        self.RAM_max = RAM_max
        self.RAM_last = RAM_last
        
        try:
            self.RAM_leakage = self.RAM_last - self.RAM_start
        except:
            self.RAM_leakage = None

    
    def getStart(self):
        return self.RAM_start
    
    def getPeak(self):
        return self.RAM_max
    
    def getLast(self):
        return self.RAM_last

    def __str__(self):
        return "RAM, start: " + str(self.RAM_start) + ", last: " + str(self.RAM_last) + ", max: " + str(self.RAM_max)



class GPUsRAM_Info_Cls():
    
    def __init__(self, GPU_RAMs_start_dict, GPU_RAMs_max_dict, GPU_RAMs_last_dict):
        
        self.GPU_id_2_RAM_Info_dict = {}
        
        self.GPU_ids = sorted(GPU_RAMs_max_dict.keys())
        
        for GPU_id in self.GPU_ids:
            
            self.GPU_id_2_RAM_Info_dict[GPU_id] = RAM_Info_Cls(
                GPU_RAMs_start_dict.get(GPU_id, None), 
                GPU_RAMs_max_dict.get(GPU_id, None), 
                GPU_RAMs_last_dict.get(GPU_id, None)
                )


    def getGPUsIds(self):
        return self.GPU_ids[:]
    

    
    def getStart(self, GPU_id):
        return self.GPU_id_2_RAM_Info_dict[GPU_id].getStart()
    
    def getPeak(self, GPU_id):
        return self.GPU_id_2_RAM_Info_dict[GPU_id].getPeak()
    
    def getLast(self, GPU_id):
        return self.GPU_id_2_RAM_Info_dict[GPU_id].getLast()
    





