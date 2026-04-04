from pydantic import BaseModel, EmailStr
# For Register
#input
class RegisterRequest(BaseModel):
    name:str
    email :EmailStr
    password :str
#output
class RegisterResponse(BaseModel):
    message:str
# For login
#input
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
#output — returns a token
class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"  # default value
#For Get me
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_verified: bool

    model_config = {"from_attributes": True}  # allows reading from DB object directly
# For send-code
#input
class SendCodeRequest(BaseModel):
    email: EmailStr
# For verify
#input
class VerifyRequest(BaseModel):
    email: EmailStr
    code: str  # str not int — preserves leading zeros e.g. "007123"
# Both return just a message
class MessageResponse(BaseModel):
    message: str
