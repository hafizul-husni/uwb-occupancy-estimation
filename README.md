# Occupancy Estimation using UWB Radar and Machine Learning

Final Year Project, Bachelor of Mechatronic Engineering (Hons), Universiti Sains Malaysia, 2026.

A privacy-preserving system that counts how many people (0 to 3) are in a room using ultra-wideband (UWB) radio signals and machine learning. No cameras, no images, and occupants do not need to carry any device.

## Key results

| Approach | Data per frame | Firmware change | Macro F1 (session-level 5-fold CV) |
|---|---|---|---|
| DIAG baseline (distance + RSSI) | 2 values | None | 60.8% ± 10.5 |
| Truncated CIR | 64 taps | Required | 70.5% |
| **Full CIR, RF + SVM + CNN ensemble** | **1016 taps** | **Required** | **86.7% ± 8.0** |

- Full Channel Impulse Response (CIR) beat the default diagnostic output by about **26 percentage points** under the same leakage-free evaluation.
- Capturing only 64 of the 1016 taps (6%) was not enough. The occupancy information lives in the multipath tail after the direct-path peak (tap 743).
- This is the first DIAG vs CIR comparison on the Qorvo DWM3001CDK platform.

## System overview

```
Board A (Initiator) ──UWB TWR frames, Ch5 6.5 GHz──► Board B (Listener)
                                                       │ modified firmware
                                                       │ 1016-tap CIR via SEGGER RTT
                                                       ▼
                                           Python acquisition + parsing (HDF5)
                                                       │
                                     Feature extraction (978 features/window)
                                                       │
                                  Random Forest | SVM (RBF) | 2D CNN → soft voting
```

## Embedded / firmware work

- Hardware: 2x Qorvo DWM3001CDK (DW3110 UWB transceiver + Nordic nRF52833 MCU), FreeRTOS CLI firmware from DW3_QM33_SDK.
- Modified the Listener firmware to read the full 1016-tap Ipatov CIR accumulator (`dwt_readaccdata()`), enlarging the CIR and output buffers.
- Moved data output from UART (115200 baud) to **SEGGER J-Link RTT** for higher throughput.
- Fixed a CMake linker-script path issue during the build.
- Final build: 82.4% of 128 KB RAM, 45.0% of 504 KB flash.
- Wrote a Python two-line state-machine parser for the UART diagnostic output.

## Machine learning

- Dataset: 40 sessions, balanced across 4 classes (0, 1, 2, 3 persons), ~84 full-CIR frames per session. Participants sat, stood, and walked; positions varied between sessions.
- Features: multipath region statistics, tail energy in delay sub-bands, frame-to-frame motion, profile shape.
- Models: Random Forest, SVM (RBF), 2D CNN, and a soft-voting ensemble (scikit-learn).
- Evaluation: **session-level** 5-fold cross-validation, so windows from one recording never appear in both train and test sets. A window-level split inflated the DIAG score to 83.0% through temporal leakage.

| Class | Precision | Recall | F1 |
|---|---|---|---|
| Empty | 99% | 98% | 98% |
| 1 person | 89% | 69% | 74% |
| 2 persons | 80% | 94% | 86% |
| 3 persons | 87% | 90% | 88% |

## Limitations and future work

- 1 vs 2 persons is the hardest boundary: tail energy rises ~31% from empty to 1 person, but changes only ~2.6% from 1 to 2.
- Single room, single board placement. Generalisation to other rooms is not tested.
- Next steps: CIR capture on both boards, a larger dataset for the CNN, and on-device (TinyML) inference on the nRF52833.

## Tech stack

C, FreeRTOS, nRF52833, Qorvo DW3110 SDK, SEGGER J-Link / RTT, CMake, Python, NumPy, h5py, scikit-learn, CNN.

## Note on source code

The original source code from this project was lost. This repository documents the system design, methodology, and results from the thesis. A rebuilt version of the analysis pipeline may be added later.
