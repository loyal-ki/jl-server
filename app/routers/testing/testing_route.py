from fastapi import APIRouter

from youtube_transcript_api import YouTubeTranscriptApi

from app.core.schema.base_response import BaseResponse

# from core.translations.translations import translate_en2vi

router = APIRouter(prefix="/testing")

@router.get(
    "/videoId",
)
def get_video_id():
    youtubeID = "7bCIHLgKJnU"

    srt = YouTubeTranscriptApi.get_transcript(youtubeID)

    # for item in srt:
    #     item["vi_translation"] = translate_en2vi(item["text"])

    # data_response = {
    #     "youtubeID" : youtubeID,
    #     "srt": srt,
    # }
    # return json_response({**SuccessResponse.default(), "data": srt})
    return BaseResponse.success(
            srt,
            msg="Get video successfully",
        )


# @router.get(
#     '/speech',
# )
# def get_speech_api():

#     processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
#     model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
#     vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")

#     inputs = processor(text="Hello, my dog is cute", return_tensors="pt")

#     # load xvector containing speaker's voice characteristics from a dataset
#     embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
#     speaker_embeddings = torch.tensor(embeddings_dataset[3000]["xvector"]).unsqueeze(0)

#     speech = model.generate_speech(inputs["input_ids"], speaker_embeddings, vocoder=vocoder)

#     sf.write("speech.wav", speech.numpy(), samplerate=16000)


#     return json_response({
#         **SuccessResponse.default(),
#     })
