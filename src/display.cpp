#include <display.hpp>
#include <iostream>

Display::Display() {
    // yes, this is a bit of a hack, but it works and
    // wiringPi can't turn on the display
    system("python init_display.py");

    mcp23017Setup(AF_BASE, 0x20);
    this->lcd = lcdInit(2, 16, 4, AF_RS, AF_E, AF_DB4,
            AF_DB5, AF_DB6, AF_DB7, 0, 0, 0, 0);
    this->cursor_row = 0;
    this->cursor_col = 0;
    lcdDisplay(this->lcd, true);
    lcdHome(this->lcd);
    lcdClear(this->lcd);
    for (int row = 0; row < NUM_ROWS; ++row) {
        for (int col = 0; col < NUM_COLS; ++col) {
            curr_text[row][col] = ' ';
        }
    }
    this->clear();
}

void Display::clear() {
    this->clear_curr_text();
    this->update();
}

void Display::clear_curr_text() {
    for (int row = 0; row < NUM_ROWS; ++row) {
        for (int col = 0; col < NUM_COLS; ++col) {
            this->curr_text[row][col] = ' ';
        }
    }
    
}

void Display::update() {
    // for (int row = 0; row < NUM_ROWS; ++row) {
    //     for (int col = 0; col < NUM_COLS; ++col) {
    //         // only update if changed
    //         if (this->curr_text[row][col] != this->curr_text[row][col]) {
    //             this->curr_text[row][col] = this->curr_text[row][col];
    //             lcdPosition(this->lcd, col, row);
    //             lcdPutchar(this->lcd, this->curr_text[row][col]);
    //         }
    //     }
    // }
    char string[33];
    int i = 0;
    for (int row = 0; row < NUM_ROWS; ++row) {
        for (int col = 0; col < NUM_COLS; ++col) {
            string[i] = this->curr_text[row][col];
            i++;
        }
    }
    string[32] = '\0';
    lcdPosition(this->lcd, 0, 0);
    lcdPuts(this->lcd, string);
    lcdPosition(this->lcd, this->cursor_col, this->cursor_row);
}

void Display::message(std::string message) {
    this->clear_curr_text();
    int row = 0;
    int col = 0;
    for (char c : message) {
        if (c == '\n' || col >= NUM_COLS) {
            row++;
            col = 0;
            continue;
        } else if (row >= NUM_ROWS) {
            break;
        }
        this->curr_text[row][col] = c;
        col++;
    }
    this->update();
}

void Display::set_row(std::string text, int row) {
    for (size_t i = 0; i < text.length(); ++i) {
        if (i >= NUM_COLS) {
            break;
        }
        this->curr_text[row][i] = text[i];
    }
    this->update();
}

void Display::set_char(char c, int row, int col) {
    this->curr_text[row][col] = c;
    this->update();
}

void Display::set_cursor_position(int row, int col) {
    this->cursor_row = row;
    this->cursor_col = col;
    lcdPosition(this->lcd, this->cursor_col, this->cursor_row);
}

void Display::set_cursor_enabled(bool val) {
    this->cursor_enabled = val;
    lcdCursor(this->lcd, val);
}

void Display::set_cursor_blink_enabled(bool val) {
    this->cursor_blink_enabled = val;
    lcdCursorBlink(this->lcd, val);
}

