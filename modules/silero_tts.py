import torch
import sounddevice as sd
import  time
import soundfile as sf
import io

class TextToSpeech:
    def __init__(self, lang='ru', speaker='baya'):
        models = {'ru':'v3_1_ru', 'en':'v3_en'}
        self.language = lang
        self.model_id = models[lang]
        self.device = torch.device('cpu')
        self.sample_rate = 48000
        self.speaker = speaker
        self.put_accent=True
        self.put_yo=True


    def split_text(self, text, max_length):
        words = text.split()
        result = []
        current_chunk = ""

        for word in words:
            if len(current_chunk) + len(word) + 1 <= max_length:
                if current_chunk:
                    current_chunk += " "
                current_chunk += word
            else:
                result.append(current_chunk)
                current_chunk = word

        if current_chunk:
            result.append(current_chunk)

        return result


    def  transformation(self, text):
        model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                            model='silero_tts',
                                            language=self.language,
                                            speaker=self.model_id)
        model.to(self.device)  # gpu or cpu
        audio = model.apply_tts(text=text,
                                speaker=self.speaker,
                                sample_rate=self.sample_rate,
                                put_accent=self.put_accent,
                                put_yo=self.put_yo)
        return audio


    def core(self, text, max_length=800):
        result_chunks = self.split_text(text, max_length)

        audio_tracks = []

        # Сгенерируйте аудиодорожки для каждой части и добавьте их в список
        for chunk in result_chunks[:3]:
            print(chunk)
            audio = self.transformation(str(chunk))
            audio_tracks.append(audio)

        # Объедините аудиодорожки в одно
        audio = torch.cat(audio_tracks)
        return audio


    def play_audio(self, audio):
        sd.play(audio, self.sample_rate)
        time.sleep(len(audio)/self.sample_rate)
        sd.stop()

    
    def save_audio(self, audio, filename):
        sf.write(f'{filename}.wav', audio, self.sample_rate)


    def audio_bytes(self, audio):
        with io.BytesIO() as f:
            sf.write(f, audio, samplerate=44100, format='WAV')
            # Читаем байты из файла
            f.seek(0)
            audio_bytes = f.read()
        return audio_bytes


#tts = TextToSpeech()
#audio = tts.transformation('Приветики, владислэвчик!')
#tts.play_audio(audio)
#tts.save_audio(audio)