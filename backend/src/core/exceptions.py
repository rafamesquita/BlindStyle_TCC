class ServiceError(Exception):
    pass

class ItemNotFoundError(ServiceError):
    pass

class UnauthorizedError(ServiceError):
    pass

class ValidationError(ServiceError):
    pass

class BusinessError(ServiceError):
    pass

class DatabaseError(ServiceError):
    pass