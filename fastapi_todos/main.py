from fastapi import FastAPI

app = FastAPI()

# http://taco-randomizer.herokuapp.com/random/


@app.get("/")
async def root():
    return {"message": "Hello World!"}
