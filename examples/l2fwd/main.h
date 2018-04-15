#include <stdint.h>
#include <time.h>

typedef struct sending_batch
{
    uint8_t number;
    uint32_t count;
} sending_batch;

typedef struct receiving_batch
{
    uint32_t count;
    struct timespec init_time;
} receiving_batch;

typedef enum Mode
{
    INT_SOURCE,
    INT_SINK
} Mode;