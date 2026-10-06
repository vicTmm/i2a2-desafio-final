"""Substitui a narração preservando as imagens; requer edge-tts e FFmpeg."""
import asyncio
import argparse
import json
from pathlib import Path
import re
import subprocess


def run(args):
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr[-5000:])
    return result


def duration(ffmpeg, path):
    result = subprocess.run([str(ffmpeg), '-i', str(path)], capture_output=True, text=True)
    match = re.search(r'Duration: (\d+):(\d+):([\d.]+)', result.stderr)
    if not match:
        raise ValueError(f'Duração indisponível: {path}')
    h, m, s = map(float, match.groups())
    return h * 3600 + m * 60 + s


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--voice', default='pt-BR-AntonioNeural')
    parser.add_argument('--timings', type=Path, default=Path('tmp/video/narracao.json'))
    parser.add_argument('--reuse-audio', action='store_true', help='Reutiliza os trechos gerados em tmp/dubbing')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    ffmpeg = root / 'node_modules/ffmpeg-static/ffmpeg'
    video = root / 'Projeto_Final_Artefatos/InsurMinds_Projeto_Final.mp4'
    work = root / 'tmp/dubbing'
    work.mkdir(parents=True, exist_ok=True)
    segments = json.loads(args.timings.read_text())
    total = duration(ffmpeg, video)
    inputs, filters = [], []
    for i, segment in enumerate(segments):
        import edge_tts
        audio = work / f'narracao-{i}.mp3'
        if not args.reuse_audio:
            asyncio.run(edge_tts.Communicate(segment['narration'], args.voice,
                                           rate='+8%', pitch='+3Hz').save(str(audio)))
        seconds = duration(ffmpeg, audio)
        end = segments[i + 1]['offset'] if i + 1 < len(segments) else total
        available = end - segment['offset'] - 0.25
        if available <= 0:
            raise ValueError('Intervalo de narração inválido')
        speed = max(1, seconds / available)
        if speed > 2:
            raise ValueError('Narração longa demais para o intervalo')
        inputs.extend(['-i', str(audio)])
        filters.append(f'[{i+1}:a]atempo={speed:.6f},loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000,aformat=channel_layouts=mono,adelay={round(segment["offset"]*1000)}:all=1[a{i}]')
        print(f'Trecho {i+1}: {seconds:.2f}s; intervalo {available:.2f}s; velocidade {speed:.3f}', flush=True)
    filters.append(''.join(f'[a{i}]' for i in range(len(segments))) + f'amix=inputs={len(segments)}:normalize=0,apad[audio]')
    target = work / 'InsurMinds_Projeto_Final.mp4'
    run([str(ffmpeg), '-y', '-i', str(video), *inputs, '-filter_complex', ';'.join(filters), '-map', '0:v', '-map', '[audio]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '96k', '-t', str(total), '-movflags', '+faststart', str(target)])
    if abs(duration(ffmpeg, target) - total) > 0.1:
        raise ValueError('Duração do vídeo alterada')
    target.replace(video)
    print(f'Vídeo atualizado: {args.voice}; {total:.2f}s')


if __name__ == '__main__':
    main()
