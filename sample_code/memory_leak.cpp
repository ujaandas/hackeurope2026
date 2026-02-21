#include <cstdlib>
#include <iostream>
#include <cstring>

void processData(int n) {
    for (int i = 0; i < n; i++) {
        int* buffer = new int[1024];
        for (int j = 0; j < 1024; j++) {
            buffer[j] = i * j;
        }
        std::cout << "Processed batch " << i << std::endl;
        // Missing delete[] buffer!
    }

    char* data = (char*)malloc(4096);
    memset(data, 0, 4096);
    std::cout << "Data allocated at: " << (void*)data << std::endl;
    // Missing free(data)!
}

int main() {
    processData(100);
    return 0;
}
