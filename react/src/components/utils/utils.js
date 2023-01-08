// Return a function to fetch more data from a paginated API end point
const fetchPaginatedData =
  (data, setData, setMoreExists, nextUrl, setNextUrl) => () => {
    setMoreExists(false);
    fetch(nextUrl)
      .then((res) => res.json())
      .then((result) => {
        let hasMore = false;
        let { next } = result;
        if (next) {
          hasMore = true;
        } else {
          next = '';
        }
        setData(data.concat(result.results));
        setNextUrl(`/${next.replace(/^(?:\/\/|[^/]+)*\//, '')}`);
        setMoreExists(hasMore);
      });
  };

function addZero(i) {
  let res = i;
  if (i < 10) {
    res = `0${i}`;
  }
  return res;
}

export { fetchPaginatedData, addZero };
