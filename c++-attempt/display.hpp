#ifndef DISPLAY_H
#define DISPLAY_H 

#include <mcp23017.h>
#include <lcd.h>
#include <string>

// Paramaters for the Adafruit Char LCD Plate
#define AF_BASE         100
#define AF_RED          (AF_BASE + 6)
#define AF_GREEN        (AF_BASE + 7)
#define AF_BLUE         (AF_BASE + 8)

#define AF_E            (AF_BASE + 13)
#define AF_RW           (AF_BASE + 14)
#define AF_RS           (AF_BASE + 15)

#define AF_DB4          (AF_BASE + 12)
#define AF_DB5          (AF_BASE + 11)
#define AF_DB6          (AF_BASE + 10)
#define AF_DB7          (AF_BASE +  9)

#define AF_SELECT       (AF_BASE +  0)
#define AF_RIGHT        (AF_BASE +  1)
#define AF_DOWN         (AF_BASE +  2)
#define AF_UP           (AF_BASE +  3)
#define AF_LEFT         (AF_BASE +  4)

const int NUM_ROWS = 2;
const int NUM_COLS = 16;

class Display {

public:
    
    Display();

    void clear();
    void message(std::string message);
    void set_row(std::string text, int row);
    void set_char(char c, int row, int col);
    void set_cursor_position(int row, int col);
    void set_cursor_enabled(bool val);
    void set_cursor_blink_enabled(bool val);

private:
    
    /*
     * The text currently on the display.
     */
    char curr_text[NUM_ROWS][NUM_COLS];

    int lcd;
    int cursor_row;
    int cursor_col;
    bool cursor_enabled;
    bool cursor_blink_enabled;

    /*
     * Transfers the curr_text grid to the
     * display, updating the curr_text.
     * Restores the cursor position when done.
     */
    void update();

    /*
     * Clears the curr_text grid.
     */
    void clear_curr_text();
};

#endif /* ifndef DISPLAY_H */
