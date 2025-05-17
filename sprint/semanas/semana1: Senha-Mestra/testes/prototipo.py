import json as j
import hashlib

def definirSenhaMestra(config: dict):
    senhaMestra = input("Qual será a nova senha mestra? ").encode()
    with open('garracio.json', 'w') as f:
        config['senhaMestra'] = hashlib.sha256(senhaMestra).hexdigest   ()
        j.dump(config, f, indent=4)

def lerSenhaMestra():
    with open('garracio.json', 'r') as f: config = j.load(f)
    return config

def main():
    senhaMestra = input("Digite a senha mestra: ")

    config = lerSenhaMestra()

    if senhaMestra == "def": definirSenhaMestra(config)

    senhaMestraReal = config['senhaMestra']
    if hashlib.sha256(senhaMestra.encode()).hexdigest() == senhaMestraReal:
        print("Boa")
    else:
        print("errou")

if __name__ == "__main__": main()
