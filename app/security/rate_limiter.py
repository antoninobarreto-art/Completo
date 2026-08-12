import time
from collections import defaultdict
from threading import Lock

class InMemoryRateLimiter:
    """
    Rate Limiter em memória com Janela Deslizante (Sliding Window).
    Evita concorrência e escritas constantes de I/O no arquivo do SQLite.
    """
    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
        self.lock = Lock()

    def is_allowed(self, identifier: str) -> bool:
        """
        Verifica se a chave (ex: IP ou E-mail) pode realizar a requisição.
        Limpa automaticamente registros antigos fora da janela de tempo.
        """
        now = time.time()
        window_start = now - self.window_seconds

        with self.lock:
            # Filtra requisições que caíram fora da janela
            timestamps = [ts for ts in self.requests[identifier] if ts > window_start]
            
            if len(timestamps) >= self.max_requests:
                self.requests[identifier] = timestamps
                return False
            
            timestamps.append(now)
            self.requests[identifier] = timestamps
            return True

    def reset(self, identifier: str):
        """Reseta as tentativas para uma chave (ex: após login bem-sucedido)."""
        with self.lock:
            if identifier in self.requests:
                del self.requests[identifier]

# Instância global para limitar tentativas de Login (ex: máx 5 tentativas por minuto por IP/E-mail)
login_rate_limiter = InMemoryRateLimiter(max_requests=5, window_seconds=60)
