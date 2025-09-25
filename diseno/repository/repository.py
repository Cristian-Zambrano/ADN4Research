class DesignRepository:
    def __init__(self):
        self.storage = {}

    def save(self, design_id, data):
        self.storage[design_id] = data
        return design_id