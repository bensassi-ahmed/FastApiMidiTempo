from io import BytesIO
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import pretty_midi
from typing import Dict, Any
import uvicorn

app = FastAPI(
    title="MIDI Analysis API",
    description="API for analyzing MIDI files and extracting musical metrics",
    version="1.0.0",
)


@app.post(
    "/",
    response_model=Dict[str, Any],
    summary="Analyze MIDI file",
    description="Process a MIDI file and return musical analysis results",
    responses={
        200: {"description": "Successful analysis"},
        400: {"description": "Invalid file format or processing error"},
        413: {"description": "File too large"},
    }
)
async def analyze_midi(
        midi_file: UploadFile = File(
            ...,
            description="MIDI file to analyze (supported formats: .mid, .midi)",
            max_size=10_000_000,  # 10MB limit
        )
) -> JSONResponse:
    """
    Analyze a MIDI file and extract musical metrics

    Args:
        midi_file: Uploaded MIDI file

    Returns:
        JSON response containing analysis results

    Raises:
        HTTPException: If file processing fails
    """
    try:
        # Validate file type
        if not midi_file.filename.lower().endswith(('.mid', '.midi')):
            raise ValueError("Invalid file format. Only MIDI files are accepted.")

        # Read and process file
        file_content = await midi_file.read()
        midi_data = pretty_midi.PrettyMIDI(BytesIO(file_content))

        # Extract tempo information
        tempo_changes = midi_data.get_tempo_changes()
        tempos = tempo_changes[1]

        # Prepare response data
        response_data = {
            "filename": midi_file.filename,
            "tempo": tempos[0] if len(tempos) > 0 else 120,
            "tempo_changes": {
                "times": tempo_changes[0].tolist(),
                "values": tempos.tolist()
            },
            "duration": midi_data.get_end_time(),
            "instruments": len(midi_data.instruments)
        }

        return JSONResponse(
            content=response_data,
            status_code=200
        )

    except ValueError as ve:
        raise HTTPException(
            status_code=400,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error processing MIDI file: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)