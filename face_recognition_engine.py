"""
face_recognition_engine.py
──────────────────────────
Face recognition layer for Hospital PMS.

Uses:
  • face_recognition  (dlib-based, high accuracy)
  • OpenCV (cv2)      (webcam capture + frame display)

Workflow:
  1. PatientFaceEngine.register_face(patient_id, frame)
       → encode face → store in DB as binary blob
  2. PatientFaceEngine.identify_from_frame(frame)
       → compare against all stored encodings
       → return (patient_id, patient_name, confidence) or None
"""

from __future__ import annotations

import io
import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

# ── lazy imports so the app still launches if libs are missing ──────────── #
try:
    import face_recognition as fr
    import cv2
    FACE_LIBS_OK = True
except ImportError:
    FACE_LIBS_OK = False
    logger.warning(
        "face_recognition or opencv-python not installed. "
        "Run:  pip install face_recognition opencv-python"
    )


@dataclass
class FaceMatch:
    patient_id: int
    patient_name: str
    confidence: float          # 0.0 (worst) → 1.0 (perfect)
    frame: Optional[np.ndarray] = None   # annotated frame for display


class FaceNotFoundError(Exception):
    """Raised when no face is detected in a frame."""


class PatientFaceEngine:
    """
    Manages face encodings linked to patient records.

    Encodings are stored as numpy float64 arrays serialised with np.save
    and kept in the 'face_encodings' table of the same SQLite database.
    """

    TOLERANCE = 0.50        # lower = stricter (0.6 is face_recognition default)
    FRAME_SCALE = 0.5       # downscale for faster detection

    def __init__(self, db_conn) -> None:
        """
        Parameters
        ----------
        db_conn : sqlite3.Connection
            Shared connection from database.Database._conn
        """
        self._conn = db_conn
        self._create_table()
        # in-memory cache: {patient_id: np.ndarray encoding}
        self._encodings: dict[int, tuple[str, np.ndarray]] = {}
        self._load_all_encodings()

    # ------------------------------------------------------------------ #
    #  Schema                                                               #
    # ------------------------------------------------------------------ #
    def _create_table(self) -> None:
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS face_encodings (
                patient_id  INTEGER PRIMARY KEY
                            REFERENCES patients(id) ON DELETE CASCADE,
                patient_name TEXT NOT NULL,
                encoding    BLOB NOT NULL,
                created_at  TEXT DEFAULT (datetime('now'))
            )
        """)
        self._conn.commit()

    # ------------------------------------------------------------------ #
    #  Persistence helpers                                                  #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _encode_to_blob(encoding: np.ndarray) -> bytes:
        buf = io.BytesIO()
        np.save(buf, encoding)
        return buf.getvalue()

    @staticmethod
    def _blob_to_encode(blob: bytes) -> np.ndarray:
        return np.load(io.BytesIO(blob))

    def _load_all_encodings(self) -> None:
        """Load all stored encodings into memory cache."""
        self._encodings.clear()
        rows = self._conn.execute(
            "SELECT patient_id, patient_name, encoding FROM face_encodings"
        ).fetchall()
        for pid, name, blob in rows:
            self._encodings[pid] = (name, self._blob_to_encode(blob))
        logger.info("Loaded %d face encodings", len(self._encodings))

    # ------------------------------------------------------------------ #
    #  Public API                                                           #
    # ------------------------------------------------------------------ #
    def libs_available(self) -> bool:
        return FACE_LIBS_OK

    def registered_count(self) -> int:
        return len(self._encodings)

    def is_registered(self, patient_id: int) -> bool:
        return patient_id in self._encodings

    # ── Registration ──────────────────────────────────────────────────── #
    def register_face(
        self,
        patient_id: int,
        patient_name: str,
        frame: np.ndarray,
    ) -> None:
        """
        Detect a face in *frame* and store its encoding for *patient_id*.

        Raises
        ------
        FaceNotFoundError  if no face is detected in frame.
        RuntimeError       if face_recognition library is missing.
        """
        if not FACE_LIBS_OK:
            raise RuntimeError("face_recognition library not installed.")

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        locations = fr.face_locations(rgb, model="hog")
        if not locations:
            raise FaceNotFoundError("No face detected in the captured frame.")

        # Use only the first (largest) face
        encoding = fr.face_encodings(rgb, known_face_locations=[locations[0]])[0]
        blob = self._encode_to_blob(encoding)

        self._conn.execute("""
            INSERT INTO face_encodings (patient_id, patient_name, encoding)
            VALUES (?, ?, ?)
            ON CONFLICT(patient_id) DO UPDATE SET
                patient_name = excluded.patient_name,
                encoding     = excluded.encoding,
                created_at   = datetime('now')
        """, (patient_id, patient_name, blob))
        self._conn.commit()

        # Update in-memory cache
        self._encodings[patient_id] = (patient_name, encoding)
        logger.info("Registered face for patient %d (%s)", patient_id, patient_name)

    def delete_face(self, patient_id: int) -> None:
        self._conn.execute(
            "DELETE FROM face_encodings WHERE patient_id=?", (patient_id,))
        self._conn.commit()
        self._encodings.pop(patient_id, None)

    # ── Identification ─────────────────────────────────────────────────── #
    def identify_from_frame(self, frame: np.ndarray) -> Optional[FaceMatch]:
        """
        Detect faces in *frame* and match against stored encodings.

        Returns the best FaceMatch or None if no match is found.
        The returned FaceMatch.frame contains the frame annotated with
        a bounding box and patient name.
        """
        if not FACE_LIBS_OK or not self._encodings:
            return None

        # Downscale for speed
        small = cv2.resize(frame, (0, 0), fx=self.FRAME_SCALE, fy=self.FRAME_SCALE)
        rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

        locations = fr.face_locations(rgb_small, model="hog")
        if not locations:
            return None

        unknowns = fr.face_encodings(rgb_small, known_face_locations=locations)
        if not unknowns:
            return None

        # Build known lists
        known_ids   = list(self._encodings.keys())
        known_names = [self._encodings[pid][0] for pid in known_ids]
        known_encs  = [self._encodings[pid][1] for pid in known_ids]

        best_match: Optional[FaceMatch] = None

        for unknown_enc, loc in zip(unknowns, locations):
            distances = fr.face_distance(known_encs, unknown_enc)
            best_idx  = int(np.argmin(distances))
            distance  = float(distances[best_idx])

            if distance > self.TOLERANCE:
                continue

            confidence = round(1.0 - distance, 3)
            pid  = known_ids[best_idx]
            name = known_names[best_idx]

            # Scale location back to original frame
            scale = 1.0 / self.FRAME_SCALE
            top, right, bottom, left = [int(v * scale) for v in loc]

            # Annotate frame
            annotated = frame.copy()
            cv2.rectangle(annotated, (left, top), (right, bottom),
                          (0, 201, 167), 2)
            label = f"{name}  {confidence*100:.0f}%"
            cv2.rectangle(annotated, (left, bottom - 28), (right, bottom),
                          (0, 201, 167), cv2.FILLED)
            cv2.putText(annotated, label,
                        (left + 6, bottom - 8),
                        cv2.FONT_HERSHEY_DUPLEX, 0.55,
                        (15, 25, 35), 1)

            if best_match is None or confidence > best_match.confidence:
                best_match = FaceMatch(
                    patient_id=pid,
                    patient_name=name,
                    confidence=confidence,
                    frame=annotated,
                )

        return best_match

    # ── Camera helpers ─────────────────────────────────────────────────── #
    @staticmethod
    def open_camera(index: int = 0) -> "cv2.VideoCapture":
        if not FACE_LIBS_OK:
            raise RuntimeError("opencv-python not installed.")
        cap = cv2.VideoCapture(index)
        if not cap.isOpened():
            raise RuntimeError(
                f"Cannot open camera at index {index}. "
                "Check that no other app is using the webcam."
            )
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        return cap

    @staticmethod
    def capture_frame(cap: "cv2.VideoCapture") -> Optional[np.ndarray]:
        """Read one frame; return None on failure."""
        ret, frame = cap.read()
        return frame if ret else None
