#include <display.hpp>

Display::Display() {
    mcp23017Setup(AF_BASE, 0x20);
    lcd = lcdInit(2, 16, 4, AF_RS, AF_E, AF_DB4, AF_DB5, AF_DB6, AF_DB7, 0, 0, 0, 0);
    for (int row = 0; row < NUM_ROWS; ++row) {
        for (int col = 0; col < NUM_COLS; ++col) {
            curr_text[row][col] = 0;
        }
    }
}

void Display::clear() {
    // TODO implement
}

void Display::message(std::string message) {
    // TODO implement
}

void Display::set_row(std::string text, int row) {
    // TODO implement
}

void Display::set_char(char c, int row, int col) {
    // TODO implement
}

void Display::set_cursor_position(int row, int col) {
    // TODO implement
}

void Display::set_cursor_enabled(bool val) {
    // TODO implement
}

void Display::set_cursor_blink_enabled(bool val) {
    // TODO implement
}

