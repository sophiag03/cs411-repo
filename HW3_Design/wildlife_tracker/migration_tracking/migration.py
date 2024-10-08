from typing import Any

class Migration:

    def __init__ (self, 
                  current_location: str,
                  migration_id: int,
                  start_date: str,
                  status: str = "Scheduled") -> None:
        
        self.current_location = current_location
        self.migration_id = migration_id
        self.start_date = start_date
        self.status = status


    def cancel_migration(self, migration_id: int) -> None:
        pass

    def get_migration_details(self, migration_id: int) -> dict[str,Any]:
        pass

    def update_migration_details(self, migration_id: int, **kwargs: Any) -> None:
        pass
    
    pass