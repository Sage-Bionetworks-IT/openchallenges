from enum import Enum


class FargateCpuMemory(Enum):
    CPU_256_MEM_512 = (256, 512)
    CPU_256_MEM_1024 = (256, 1024)
    CPU_256_MEM_2048 = (256, 2048)
    CPU_512_MEM_1024 = (512, 1024)
    CPU_512_MEM_2048 = (512, 2048)
    CPU_512_MEM_3072 = (512, 3072)
    CPU_512_MEM_4096 = (512, 4096)
    CPU_1024_MEM_2048 = (1024, 2048)
    CPU_1024_MEM_3072 = (1024, 3072)
    CPU_1024_MEM_4096 = (1024, 4096)
    CPU_1024_MEM_5120 = (1024, 5120)
    CPU_1024_MEM_6144 = (1024, 6144)
    CPU_1024_MEM_7168 = (1024, 7168)
    CPU_1024_MEM_8192 = (1024, 8192)
    CPU_2048_MEM_4096 = (2048, 4096)
    CPU_2048_MEM_5120 = (2048, 5120)
    CPU_2048_MEM_6144 = (2048, 6144)
    CPU_2048_MEM_7168 = (2048, 7168)
    CPU_2048_MEM_8192 = (2048, 8192)
    CPU_2048_MEM_9216 = (2048, 9216)
    CPU_2048_MEM_10240 = (2048, 10240)
    CPU_2048_MEM_11264 = (2048, 11264)
    CPU_2048_MEM_12288 = (2048, 12288)
    CPU_2048_MEM_13312 = (2048, 13312)
    CPU_2048_MEM_14336 = (2048, 14336)
    CPU_2048_MEM_15360 = (2048, 15360)
    CPU_2048_MEM_16384 = (2048, 16384)
    CPU_4096_MEM_8192 = (4096, 8192)
    CPU_4096_MEM_9216 = (4096, 9216)
    CPU_4096_MEM_10240 = (4096, 10240)
    CPU_4096_MEM_11264 = (4096, 11264)
    CPU_4096_MEM_12288 = (4096, 12288)
    CPU_4096_MEM_13312 = (4096, 13312)
    CPU_4096_MEM_14336 = (4096, 14336)
    CPU_4096_MEM_15360 = (4096, 15360)
    CPU_4096_MEM_16384 = (4096, 16384)
    CPU_4096_MEM_30720 = (4096, 30720)
    CPU_8192_MEM_16384 = (8192, 16384)
    CPU_8192_MEM_20480 = (8192, 20480)
    CPU_8192_MEM_24576 = (8192, 24576)
    CPU_8192_MEM_28672 = (8192, 28672)
    CPU_8192_MEM_61440 = (8192, 61440)
    CPU_16384_MEM_32768 = (16384, 32768)
    CPU_16384_MEM_40960 = (16384, 40960)
    CPU_16384_MEM_49152 = (16384, 49152)
    CPU_16384_MEM_57344 = (16384, 57344)
    CPU_16384_MEM_122880 = (16384, 122880)

    @property
    def cpu(self) -> int:
        """Returns the CPU value of the pair."""
        return self.value[0]

    @property
    def memory(self) -> int:
        """Returns the memory value of the pair."""
        return self.value[1]

    @staticmethod
    def valid_combinations() -> list:
        """Returns all valid CPU and memory combinations."""
        return [(item.cpu, item.memory) for item in FargateCpuMemory]

    @staticmethod
    def is_valid(cpu: int, memory: int) -> bool:
        """Checks if a CPU and memory pair is valid."""
        return (cpu, memory) in FargateCpuMemory.valid_combinations()
