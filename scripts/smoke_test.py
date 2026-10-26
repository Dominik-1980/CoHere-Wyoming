#!/usr/bin/env python3
"""Direct Wyoming check. No Home Assistant connection or device actions."""
import argparse
import json
import socket
import wave


def send(stream, kind, data=None, payload=None):
    event = {"type": kind, "data": data or {}}
    if payload is not None:
        event["payload_length"] = len(payload)
    stream.write(json.dumps(event).encode() + b"\n")
    if payload is not None:
        stream.write(payload)
    stream.flush()


def receive(stream):
    header = stream.readline()
    if not header:
        raise RuntimeError("Wyoming service closed without a response")
    event = json.loads(header)
    extra = stream.read(event.get("data_length", 0))
    if extra:
        event.setdefault("data", {}).update(json.loads(extra))
    stream.read(event.get("payload_length", 0))
    return event


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=10324)
    p.add_argument("--wav", help="Optional 16 kHz mono PCM16 WAV to transcribe directly")
    p.add_argument("--language", default="de")
    args = p.parse_args()
    with socket.create_connection((args.host, args.port), timeout=120) as sock:
        with sock.makefile("rwb") as stream:
            send(stream, "describe")
            info = receive(stream)
            if info.get("type") != "info":
                raise RuntimeError(f"Expected info: {info}")
            print(json.dumps(info, ensure_ascii=False, indent=2))
    if args.wav:
        with wave.open(args.wav, "rb") as wav:
            if (wav.getframerate(), wav.getnchannels(), wav.getsampwidth()) != (16000, 1, 2):
                raise RuntimeError("WAV must be 16 kHz, mono, signed PCM16")
            with socket.create_connection((args.host, args.port), timeout=120) as sock:
                with sock.makefile("rwb") as stream:
                    send(stream, "transcribe", {"language": args.language})
                    send(stream, "audio-start", {"rate": 16000, "width": 2, "channels": 1})
                    while chunk := wav.readframes(1600):
                        send(stream, "audio-chunk", {"rate": 16000, "width": 2, "channels": 1}, chunk)
                    send(stream, "audio-stop")
                    result = receive(stream)
                    if result.get("type") != "transcript":
                        raise RuntimeError(f"Expected transcript: {result}")
                    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
