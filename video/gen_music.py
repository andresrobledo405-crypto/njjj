import sys, torch, scipy.io.wavfile as w
from transformers import AutoProcessor, MusicgenForConditionalGeneration
p = AutoProcessor.from_pretrained("facebook/musicgen-small")
m = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")
inp = p(text=["calm ambient electronic, soft warm pads, gentle pulse, modern tech product promo, no vocals"], padding=True, return_tensors="pt")
# 1500 tokens ~ 30 s at 50 Hz; we need 20 s
out = m.generate(**inp, do_sample=True, guidance_scale=3, max_new_tokens=1000)
sr = m.config.audio_encoder.sampling_rate
w.write(sys.argv[1], sr, out[0,0].numpy())
print("ok", sr, out.shape)
