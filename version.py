import requests

VERSION = "1.1.0"

def get_version_string():
    return VERSION

def get_version_info():
    return {
        'version': VERSION,
        'company': 'SyntaxShifter',
        'product': 'M3U VOD Downloader',
        'copyright': 'Copyright (c) 2024 SyntaxShifter'
    }

def check_for_updates():
    """
    Esta função verifica se há atualizações disponíveis.
    Por enquanto, retorna False pois não há um endpoint de verificação implementado.
    """
    return False 