import os

# many sessions share this PC: keep numpy single threaded (OpenBLAS fails to allocate otherwise)
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
