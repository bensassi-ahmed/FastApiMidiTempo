from fastapi import FastAPI, File, UploadFile, HTTPException
import pretty_midi
from io import BytesIO
from fastapi.middleware.wsgi import WSGIMiddleware

app = FastAPI()

@app.post("/")
async def analyze_midi(midi_file: UploadFile = File(...)):
    try:
        content = await midi_file.read()
        midi_data = pretty_midi.PrettyMIDI(BytesIO(content))
        tempos = midi_data.get_tempo_changes()[1]
        return {"tempo": tempos[0] if tempos else 120}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Expose the WSGI application
application = WSGIMiddleware(app)