import torchaudio
import numpy as np
import torch

def wav_to_tensor(path: str, target_sr: int = 16000) -> np.ndarray:
    waveform, sample_rate = torchaudio.load(path)  # [채널, 샘플 수]
    
    # 스테레오 → 모노 변환
    if waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)
    
    # 샘플링 레이트 변환
    if sample_rate != target_sr:
        resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=target_sr)
        waveform = resampler(waveform)
    
    # torch.Tensor → numpy 변환 및 float32 타입 보장
    np_wav = waveform.squeeze().cpu().numpy().astype(np.float32)
    tensor_wav = torch.from_numpy(np_wav)
    return tensor_wav


from speechbrain.inference.speaker import SpeakerRecognition
verification = SpeakerRecognition.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir="pretrained_models/spkrec-ecapa-voxceleb")



def voice_verify(ref, test):

    if isinstance(ref, str):
        ref = wav_to_tensor(ref) 
    
    if isinstance(test, str):
        test = wav_to_tensor(test) 
    


    score, prediction = verification.verify_batch(ref, test)

    return prediction, score



