import { timeUnicode, formatDate, formatTime } from '../utils/format.jsx';

describe('format utilities', () => {
  describe('timeUnicode', () => {
    it('returns correct clock emoji for hour 0 (midnight)', () => {
      expect(timeUnicode('00:00:00')).toBe('\u{1F55B}');
    });

    it('returns correct clock emoji for hour 1', () => {
      expect(timeUnicode('01:00:00')).toBe('\u{1F550}');
    });

    it('returns correct clock emoji for hour 12 (noon)', () => {
      expect(timeUnicode('12:00:00')).toBe('\u{1F55B}');
    });

    it('returns correct clock emoji for hour 13 (1 PM)', () => {
      expect(timeUnicode('13:00:00')).toBe('\u{1F550}');
    });

    it('returns correct clock emoji for hour 23 (11 PM)', () => {
      expect(timeUnicode('23:00:00')).toBe('\u{1F55A}');
    });

    it('returns correct clock emoji for hour 11 (11 AM)', () => {
      expect(timeUnicode('11:00:00')).toBe('\u{1F55A}');
    });

    it('handles time strings with minutes and seconds', () => {
      expect(timeUnicode('14:30:45')).toBe('\u{1F551}');
    });

    it('handles hour 6 correctly', () => {
      expect(timeUnicode('06:00:00')).toBe('\u{1F555}');
    });

    it('handles hour 18 (6 PM) correctly', () => {
      expect(timeUnicode('18:00:00')).toBe('\u{1F555}');
    });
  });
});

