// Return a function to fetch more data from a paginated API end point
const fetchPaginatedData =
  (data, setData, setMoreExists, nextUrl, setNextUrl) => () => {
    setMoreExists(false)
    fetch(nextUrl)
      .then((res) => res.json())
      .then((result) => {
        let hasMore = false
        if (result.next) {
          hasMore = true
        } else {
          result.next = ''
        }
        setData(data.concat(result.results))
        setNextUrl('/' + result.next.replace(/^(?:\/\/|[^/]+)*\//, ''))
        setMoreExists(hasMore)
      })
  }

export { fetchPaginatedData }
