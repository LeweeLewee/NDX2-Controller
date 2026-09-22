# Microphone integration review
21 September 2026. Datasheet-led proposal; no physical capture, wiring or standby measurements performed.

The selected Waveshare ESP32-S3-Touch-LCD-4.3B has no onboard microphone or ready-made I2S microphone connector. Recommend evaluating **one Adafruit 3421 SPH0645LM4H digital I2S microphone**, currently listed at £6.70 by [Pi Hut](https://thepihut.com/collections/audio/products/adafruit-i2s-mems-microphone-breakout-sph0645lm4h). It needs no separate analogue preamp or audio ADC board. One mono microphone is sufficient for the first tap-to-record trial; distant speech during loud music is not yet proven.

## Proposed pin access
The [official Waveshare mapping](https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3B) assigns the microSD interface GPIO11/MOSI, GPIO12/SCK, GPIO13/MISO, with card select on EXIO4. Most other pins already serve LCD, touch, USB and transceivers. The I/O expander cannot generate the continuous I2S clocks.

A [SparkFun microSD Sniffer](https://learn.sparkfun.com/tutorials/microsd-sniffer-hookup-guide/hardware-overview), sold by [SK Pang](https://www.skpang.co.uk/products/microsd-sniffer), exposes the slot's connections through a male card-shaped PCB and header. It is different from a female-socket-only microSD breakout.

Proposed use, subject to revision schematic and continuity checks:

| Microphone signal | Candidate display connection |
| --- | --- |
| BCLK | GPIO12, microSD CLK |
| WS / LRCLK | GPIO11, microSD CMD/MOSI |
| DOUT | GPIO13, microSD DAT0/MISO |
| 3V | Slot 3.3 V, after rail and pin verification |
| GND | Slot ground |
| SEL | Ground for left-channel mono |

This is an engineering inference from the pin map, not validated wiring. Do not initialise the SD driver or insert an SD card with these pins repurposed. The existing card slot's mechanical fit, adapter overhang, loading/pullups and power rail require checking before assembly. Leave other contacts unconnected. Soldering and short wiring are required.

The [ESP32-S3 I2S documentation](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/i2s.html) supports standard I2S reception. Implement with the project's pinned ESP-IDF version; verify clock/data alignment and captured PCM rather than assuming example code for another ESP32 board works unchanged. The [Adafruit pin guide](https://learn.adafruit.com/adafruit-i2s-mems-microphone-breakout/pinouts) specifies 1.6–3.6 V supply, clock, word select and data; do not connect to 5 V. Check the SPH0645 datasheet's supported clock range before choosing sample rate, and resample speech if required.

## Alternatives assessed
- [Adafruit ICS-43434 6049](https://thepihut.com/products/adafruit-i2s-mems-microphone-breakout-ics-43434): £8.60, sold out at Pi Hut. A reasonable alternative to revisit when screen stock returns; same three-signal pin-access problem remains. Do not buy both by default.
- [Adafruit PDM 4346](https://thepihut.com/products/adafruit-pdm-microphone-breakout-with-jst-sh-connector-ada4346): £4.80, five listed available. Two signal wires, but requires different PDM capture/configuration; JST-SH connector is not an I2C interface.
- Analogue microphone: would require an available suitable ADC path and noise assessment; not the first choice for this pin-constrained board.

## Validation before final integration
1. Inspect revision-matched schematic and adapter continuity; confirm 3.3 V and no conflicting driver.
2. Capture intelligible mono audio with LCD, touch and Wi-Fi active; inspect clipping, alignment and dropped samples.
3. Test normal seating distance, music playing, taps and housing vibrations.
4. Stop capture/clocks outside explicit recording and measure added standby current; decide whether a power gate is needed from evidence.
5. Place the microphone's bottom acoustic port toward an enclosure opening. Fit support without blocking it or pressing on the package. Check adapter/cable clearance.

See [UK procurement BOM](prototype-shopping-list.md) for quantities, costs, owned equipment and outstanding assembly items. This review does not change D017's selected display or claim a plug-and-play voice accessory.
