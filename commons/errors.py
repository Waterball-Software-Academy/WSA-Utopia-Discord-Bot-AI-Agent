class NotFoundException(Exception):
    def __init__(self, resource_name: str, resource_id):
        self.message = f"{resource_name} (id={str(resource_id)}) not found."
        super().__init__(self.message)
