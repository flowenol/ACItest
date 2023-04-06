.PHONY: clean all

all: acitest-C300.bin acitest-C600.bin

acitest-C300.bin: src/acitest.a65
	xa -DSERIAL_BASE=49920 -W -C -v -O ASCII -c src/acitest.a65 -l acitest-c300.label -o acitest-c300.bin

acitest-C600.bin: src/acitest.a65
	xa -DSERIAL_BASE=50688 -W -C -v -O ASCII -c src/acitest.a65 -l acitest-c600.label -o acitest-c600.bin

clean:
	rm -f acitest-*.bin acitest-*.label
