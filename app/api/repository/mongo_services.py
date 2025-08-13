from typing import Any, Dict, List, Union
from bson.json_util import dumps
from bson import ObjectId
from app.database.mongodb import get_data_from_mongodb
from pymongo import ReturnDocument

import json


class MongoService:
    def __init__(self,collection_name:str):
        if not collection_name:
            raise ValueError("Please Provide collection Name")
        self.collection = get_data_from_mongodb(collection_name)
        
        
    def custom_insert_one(self,data:Dict[str,Any]):
            return self.collection.insert_one(data)
        
    def custom_insert_many(self,data_list:List[Dict[str,Any]]):
        return self.collection.insert_many(data_list)
        
        
    def custom_find(self, filter: Dict[str, Any] = {}) -> List[Dict[str,Any]]:
            data = list(self.collection.find(filter))
            return json.loads(dumps(data))
        
    def custom_find_one(self,filter:Dict[str,Any] = {}) -> Union[Dict[str,Any],None]:
        doc = self.collection.find_one(filter)
        return json.loads(dumps(doc)) if doc else None
    
    def custom_update_many(self,filter:Dict[str,Any], updated_data:Dict[str,Any]):
        return self.collection.update_many(filter,{"$set": updated_data})
    
    def custom_update_one(self,filter:Dict[str,Any], updated_data:Dict[str,Any], upsert:bool = False):
        return self.collection.update_one(filter,{"$set": updated_data}, upsert=upsert)
            
    def custom_delete_one(self,filter:Dict[str,Any]):
        return self.collection.delete_one(filter)
    
    def custom_delete_many(self,filter:Dict[str,Any]):
        return self.collection.delete_many(filter)
    
    def custom_count_documents(self,filter:Dict[str,Any] = {}) -> int:
        return self.collection.count_documents(filter)
    
    
    
    def custom_find_by_id(self,id_str:str) -> Union[Dict[str,Any],None]:
        try:
            doc = self.collection.find_one({"_id":ObjectId(id_str)})
            return json.loads(dumps(doc)) if doc else None
        except Exception:
            return None
    
    
    def custom_aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = list(self.collection.aggregate(pipeline))
        return json.loads(dumps(results))
        
    
    def custom_replace_one(self, filter:Dict[str,Any], new_data:Dict[str,Any]):
        return self.collection.replace_one(filter,new_data)
    
    def custom_drop_collection(self):
        return self.collection.drop()
    
    def custom_findOneAndUpdate(self, filter:Dict[str,Any], update:Dict[str,Any], upsert:bool = False) -> Union[Dict[str,Any],None]:
        return self.collection.find_one_and_update(
            filter,                       
            update,                      
            upsert=upsert,                
            return_document=ReturnDocument.AFTER 
        )