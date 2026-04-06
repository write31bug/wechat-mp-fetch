"""
Generate a simple uplifting background music track using pure Python + numpy.
No external downloads needed.
"""
import numpy as np
from numpy import sin, pi, log10
import struct
import wave
import os

SAMPLE_RATE = 44100

def tone(freq, duration, volume=0.3, fade_in=0.05, fade_out=0.1):
    """Generate a single tone with envelope"""
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, False)
    signal = np.sin(2 * pi * freq * t)
    # Envelope
    fade_in_n = int(SAMPLE_RATE * fade_in)
    fade_out_n = int(SAMPLE_RATE * fade_out)
    env = np.ones(n)
    if fade_in_n > 0:
        env[:fade_in_n] = np.linspace(0, 1, fade_in_n)
    if fade_out_n > 0:
        env[-fade_out_n:] = np.linspace(1, 0, fade_out_n)
    return signal * env * volume

def chord(freqs, duration, volume=0.25):
    """Generate a chord from multiple frequencies"""
    return sum(tone(f, duration, volume / len(freqs)) for f in freqs)

def arpeggio(freqs, note_dur, total_dur, volume=0.25, up=True):
    """Generate arpeggio pattern"""
    n = int(SAMPLE_RATE * total_dur)
    out = np.zeros(n)
    t = 0
    notes = freqs if up else list(reversed(freqs))
    while t < total_dur:
        for f in notes:
            if t >= total_dur:
                break
            note_samples = int(SAMPLE_RATE * note_dur)
            t_end = min(t + note_samples, n)
            note_t = np.linspace(0, note_dur, t_end - t, False)
            note_sig = np.sin(2 * pi * f * note_t)
            fade = int(SAMPLE_RATE * min(0.05, note_dur * 0.3))
            env = np.ones(t_end - t)
            env[:fade] = np.linspace(0, 1, fade)
            env[-fade:] = np.linspace(1, 0, fade)
            out[t:t_end] += note_sig * env * volume
            t += note_samples
    return out

def pad(freqs, duration, volume=0.15):
    """Generate a warm pad sound"""
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, False)
    signal = np.zeros(n)
    for f in freqs:
        # Add slight detuning for warmth
        signal += np.sin(2 * pi * f * t) * 0.6
        signal += np.sin(2 * pi * (f * 1.001) * t) * 0.4
    # Slow fade
    fade_n = int(SAMPLE_RATE * 0.3)
    env = np.ones(n)
    env[:fade_n] = np.linspace(0, 1, fade_n)
    env[-fade_n:] = np.linspace(1, 0, fade_n)
    return signal / len(freqs) * env * volume

def kick(duration, bpm=120, volume=0.4):
    """Generate a simple kick drum"""
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, False)
    # Pitch drop
    f0 = 150
    f1 = 40
    freq_env = np.exp(-t * 20)
    freq = f1 + (f0 - f1) * freq_env
    signal = sin(2 * pi * freq * t)
    # Amplitude envelope
    amp_env = np.exp(-t * 15)
    return signal * amp_env * volume

def hihat(duration, volume=0.08):
    """Generate hi-hat"""
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, False)
    noise = np.random.randn(n)
    env = np.exp(-t * 30)
    return noise * env * volume

def clap(duration, volume=0.15):
    """Generate clap-like sound"""
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, False)
    noise = np.random.randn(n)
    env = np.zeros(n)
    # Multiple short bursts
    for offset in [0, 0.015, 0.03]:
        idx = int(offset * SAMPLE_RATE)
        if idx < n:
            dur = min(0.02, duration - offset)
            e = np.exp(-(t[idx:] - t[idx]) * 20) if idx == 0 else np.exp(-(t - t[idx]) * 20)
            e = np.concatenate([np.zeros(idx), e[:n-idx]])
            env += e
    return noise * env * volume

def make_song():
    """Create the full song"""
    # BPM = 120, beat = 0.5s
    beat = 0.5
    bar = beat * 4  # 2s per bar
    
    # Chord progression: C - G - Am - F (uplifting, common pop)
    # C major: C4=261.63, E4=329.63, G4=392.00
    # G major: G4=392, B4=493.88, D5=587.33
    # Am: A4=220, C5=261.63, E5=329.63
    # F: F4=349.23, A4=440, C5=523.25
    
    chords_seq = [
        # Bar 1-2: C major
        ([261.63, 329.63, 392.00], bar),
        ([261.63, 329.63, 392.00], bar),
        # Bar 3-4: G major  
        ([392.00, 493.88, 587.33], bar),
        ([392.00, 493.88, 587.33], bar),
        # Bar 5-6: Am
        ([220.00, 261.63, 329.63], bar),
        ([220.00, 261.63, 329.63], bar),
        # Bar 7-8: F
        ([349.23, 440.00, 523.25], bar),
        ([349.23, 440.00, 523.25], bar),
    ]
    
    # Arpeggio patterns (8th notes)
    arp_notes_C = [261.63, 329.63, 392.00, 523.25, 392.00, 329.63]
    arp_notes_G = [392.00, 493.88, 587.33, 783.99, 587.33, 493.88]
    arp_notes_Am = [220.00, 261.63, 329.63, 440.00, 329.63, 261.63]
    arp_notes_F = [349.23, 440.00, 523.25, 659.25, 523.25, 440.00]
    
    total_dur = sum(d for _, d in chords_seq) + bar  # extra bar for outro
    total_n = int(SAMPLE_RATE * total_dur)
    song = np.zeros(total_n)
    
    current_pos = 0
    for i, (chord_freqs, chord_dur) in enumerate(chords_seq):
        pos_samples = int(current_pos * SAMPLE_RATE)
        dur_n = int(chord_dur * SAMPLE_RATE)
        
        # Pad (chord)
        pad_sig = pad(chord_freqs, chord_dur, volume=0.12)
        song[pos_samples:pos_samples + dur_n] += pad_sig[:dur_n]
        
        # Arpeggio
        if i % 2 == 0:  # only on even bars for texture
            note_dur = beat / 2  # 8th note
            if i in [0, 1]:
                arp = arpeggio(arp_notes_C, note_dur, chord_dur, volume=0.1)
            elif i in [2, 3]:
                arp = arpeggio(arp_notes_G, note_dur, chord_dur, volume=0.1)
            elif i in [4, 5]:
                arp = arpeggio(arp_notes_Am, note_dur, chord_dur, volume=0.1)
            else:
                arp = arpeggio(arp_notes_F, note_dur, chord_dur, volume=0.1)
            song[pos_samples:pos_samples + dur_n] += arp[:dur_n]
        
        current_pos += chord_dur
    
    # Add drum pattern
    drum_n = int(total_dur * SAMPLE_RATE)
    drums = np.zeros(drum_n)
    
    # Simple beat: kick on 1 and 3, clap on 2 and 4, hihat on 8ths
    eighth_note = beat / 2
    current_t = 0
    bar_count = 0
    while current_t < total_dur - 0.1:
        beat_pos = (bar_count % 4)
        eighth_pos = 0
        t = current_t
        
        # Within one bar
        for e in range(8):
            if t >= total_dur:
                break
            n = int(t * SAMPLE_RATE)
            
            # Kick on 1 and 3 (1.5 and 3.5 eighth notes)
            if e in [0, 4] and bar_count < 8:
                k = kick(eighth_note, volume=0.35)
                drums[n:n+len(k)] += k
            
            # Clap on 2 and 4
            if e in [2, 6] and bar_count < 8:
                c = clap(eighth_note, volume=0.12)
                drums[n:n+len(c)] += c
            
            # Hi-hat on every 8th (quieter on off-beats)
            hh_vol = 0.06 if e % 2 == 0 else 0.03
            if bar_count < 8:
                hh = hihat(eighth_note * 0.5, volume=hh_vol)
                drums[n:n+len(hh)] += hh
            
            t += eighth_note
            eighth_pos += 1
        
        current_t += bar
        bar_count += 1
    
    # Mix drums
    song = song + drums
    
    # Normalize
    max_val = np.max(np.abs(song))
    if max_val > 0:
        song = song / max_val * 0.85
    
    return song, total_dur

def save_wav(filename, audio_data, duration):
    """Save audio data to WAV file"""
    audio_int = (audio_data * 32767).astype(np.int16)
    with wave.open(filename, 'w') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(audio_int.tobytes())

if __name__ == '__main__':
    out_dir = 'C:/Users/Administrator/.openclaw/workspace/douyin-video'
    os.makedirs(out_dir, exist_ok=True)
    
    music_file = os.path.join(out_dir, 'bgm.wav')
    print("Synthesizing background music...")
    song, duration = make_song()
    save_wav(music_file, song, duration)
    print(f"Music saved: {music_file} ({duration:.1f}s)")
