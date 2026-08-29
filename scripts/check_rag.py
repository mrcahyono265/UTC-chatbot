import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import is_user_facing_answer, unavailable_answer
from app.rag import retrieve


CHECKS = {
    "bisa benerin hp rusak nggk?": "HP",
    "bisa benerin pc nggk?": "Laptop dan Komputer",
    "jadwal pengambilan service": "Jadwal Pengambilan Unit",
    "dimana saya bisa ke UTC?": "Lokasi UTC",
    "apakah harus tahu kerusakannya": "Harus Tahu Kerusakannya",
}


def main():
    for question, expected_title in CHECKS.items():
        matches = retrieve(question)
        assert any(expected_title in match["title"] for match in matches), (question, matches)
    assert not is_user_facing_answer("Okay, the user is asking about UTC.")
    assert is_user_facing_answer("Ya, UTC menerima perbaikan komputer atau PC.")
    assert "asisten sedang ramai" in unavailable_answer("unavailable-busy").lower()
    print("rag-check-ok")


if __name__ == "__main__":
    main()
