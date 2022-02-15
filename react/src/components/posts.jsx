import React from 'react';
import InfiniteScroll from 'react-infinite-scroller';

function Comment(props) {
    return (
        <div></div>
    )
}

function Post(props) {
    return (
        <div></div>
    )
}

class Posts extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            error: null,
            posts: [],
            next_url: "/api/posts",
            count: null,
            more_exist: true,
        };
    }

    componentDidMount() {
        fetch(this.state.next_url)
            .then(res => res.json())
            .then(
                (result) => {
                    var has_more = false
                    if (result.next) {
                        has_more = true
                    }
                    this.setState({
                        next_url: result.next,
                        count: result.count,
                        posts: result.results,
                        more_exist: has_more
                    })
                },
                (error) => {
                    this.setState({
                        error
                    });
                }
            )
    }

    fetchData = () => {
        fetch(this.state.next_url)
            .then(res => res.json())
            .then(
                (result) => {
                    var has_more = false
                    if (result.next) {
                        has_more = true
                    }
                    this.setState({
                        next_url: result.next,
                        posts: this.state.posts.concat(result.results),
                        more_exist: has_more
                    })
                },
                (error) => {
                    this.setState({
                        error
                    });
                }
            )
    }

    render() {
        return <InfiniteScroll
            loadMore={this.fetchData}
            hasMore={this.state.more_exist}
            loader={<div key="-1" style={{ "textAlign": "center", "marginTop": "10%" }}><i className="fa fa-lg fa-spinner fa-spin"></i></div>}
            >
            <div className="row" key="-2">
                {
                    this.state.posts.map(function f(post) {
                        return <Post post={post} key={post.id} />
                    })
                }
            </div>
        </InfiniteScroll>
    }
}

export default Posts;
