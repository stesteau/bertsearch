#!/bin/sh
bert-serving-start -num_worker=5 -model_dir /model -max_seq_len=512 -device_map=0
