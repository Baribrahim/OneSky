import { timeUnicode, formatDate, formatTime } from '../utils/format.jsx';

describe('format utilities', () => {
  describe('timeUnicode', () => {
    it.each([
      ['00:00:00', '\u{1F55B}', 'hour 0 (midnight)'],
      ['01:00:00', '\u{1F550}', 'hour 1'],
      ['12:00:00', '\u{1F55B}', 'hour 12 (noon)'],
      ['13:00:00', '\u{1F550}', 'hour 13 (1 PM)'],
      ['23:00:00', '\u{1F55A}', 'hour 23 (11 PM)'],
      ['11:00:00', '\u{1F55A}', 'hour 11 (11 AM)'],
      ['14:30:45', '\u{1F551}', 'time strings with minutes and seconds'],
      ['06:00:00', '\u{1F555}', 'hour 6'],
      ['18:00:00', '\u{1F555}', 'hour 18 (6 PM)'],
    ])('returns correct clock emoji for %s', (timeString, expectedEmoji) => {
      expect(timeUnicode(timeString)).toBe(expectedEmoji);
    });
  });
});

