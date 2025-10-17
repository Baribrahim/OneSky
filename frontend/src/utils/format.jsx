function formatDate(dateString) {
    const date = new Date(dateString);

    const months = [
      'Jan', 'Feb', 'March', 'April', 'May', 'June',
      'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec'
    ];

    const day = date.getDate();
    const month = months[date.getMonth()];
    const year = date.getFullYear();

    const getOrdinal = (n) => {
      const s = ["th", "st", "nd", "rd"],
            v = n % 100;
      return s[(v - 20) % 10] || s[v] || s[0];
    };

    return `${month} ${day}${getOrdinal(day)} ${year}`;
  }

  function timeUnicode(time) {
      const unicode_clocks = [
      '\u{1F55B}',
      '\u{1F550}',
      '\u{1F551}',
      '\u{1F552}',
      '\u{1F553}',
      '\u{1F554}',
      '\u{1F555}',
      '\u{1F556}',
      '\u{1F557}',
      '\u{1F558}',
      '\u{1F559}',
      '\u{1F55A}',
    ];

    const hour = parseInt(time.slice(0,2)) % 12

    return unicode_clocks[hour]

  }

  function formatTime(time) {
    return time.length == 7 ? time.slice(0, 4) : time.slice(0, 5)
  }

    export { formatDate, formatTime, timeUnicode };