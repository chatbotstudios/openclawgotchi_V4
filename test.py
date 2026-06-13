try:
    from pydantic import BaseModel
except:
    from pydantic.v1 import BaseModel
class M(BaseModel):
    a: int
m = M(a=1)
try:
    print(dict(m))
except Exception as e:
    print("Error:", type(e), e)
