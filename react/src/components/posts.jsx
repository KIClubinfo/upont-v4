import React from 'react';
import InfiniteScroll from 'react-infinite-scroller';
import ReactMarkdown from 'react-markdown';
import {Comment} from './comment';
import {CommentForm} from './commentForm';


function post_logo(state) {
    if (state.post.club) {
        return (
            <div className="news-card-header-image">
                <img className="image-centered" src={state.post.club.logo_url}></img>
            </div>
        )
    }
    else {
        return (
            <div className="news-card-header-image">
                <img className="image-centered" src={state.post.author.picture_url}></img>
            </div>
        )
    }
}

function post_author(state) {
    if (state.post.club) {
        return (
            <span className="news-card-header-name">
                {state.post.club.name}
            </span>
        )
    }
    else {
        return (
            <span className="news-card-header-name">
                {state.post.author.user.first_name} {state.post.author.user.last_name}
            </span>
        )
    }
}

function post_title(state) {
    if (state.post.event_url) {
        return (
            <a href={state.post.event_url} className="news-card-header-title">{state.post.title}</a>
        )
    }
    else {
        return (
            <span className="news-card-header-title">{state.post.title}</span>
        )
    }
}

function post_illustration(state) {
    if (state.post.illustration_url) {
        return (
            <div className="news-card-images">
                <div className="news-card-carousel">
                    <div className="carousel-cell">
                        <img className="news-card_image_sized" src={state.post.illustration_url} alt=""></img>
                    </div>
                </div>
            </div>
        )
    }
}

function post_like_button(state) {
    if (state.post.user_liked) {
        return (
            <a href={state.post.dislike_url} className="news-card-button"><i className="fas fa-heart"></i></a>
        )
    }
    else {
        return (
            <a href={state.post.like_url} className="news-card-button"><i className="far fa-heart"></i></a>
        )
    }
}

class Post extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            post: props.post,
            currentStudent: props.currentStudent
        };
        this.refresh = this.refresh.bind(this);
    }

    refresh() {
        fetch("/api/posts/"+this.state.post.id+"/")
            .then(res => res.json())
            .then(
                (result) => {
                    this.setState({post: result})
                },
                (error) => {
                    this.setState({
                        error
                    });
                }
            );
    }

    render() {
        return (
            <div>
                <div className="news-card" id={this.state.post.id}>
                    <div className="news-card-header">
                        {post_logo(this.state)}
                        <div className="news-card-header-text">
                            {post_author(this.state)}
                            {post_title(this.state)}
                        </div>
                    </div>

                    <div className="news-card-content">
                        <div className="centered-div">
                            <a href={this.state.post.edit_url}><button className="button blue-button">Éditer</button></a>
                        </div>
                        <ReactMarkdown>{this.state.post.content}</ReactMarkdown>
                    </div>

                    {post_illustration(this.state)}


                    <div className="news-card-actions">
                        <div className="news-card-buttons">
                            {post_like_button(this.state)}
                        </div>
                        <div className="news-card-popularity">
                            <span><i className="fas fa-heart" style={{ color: 'red' }}></i> {this.state.post.total_likes}</span>
                            <span><i className="fas fa-comment" style={{ color: 'rgb(0, 153, 255)' }}></i> {this.state.post.total_comments}</span>
                        </div>
                    </div>

                    <div className="news-card-comments" style={{display: "block"}}>
                        {
                            this.state.post.comments.map(function f(comment) {
                                return <Comment comment={comment} key={comment.id} />
                            })
                        }
                        <CommentForm post={this.state.post} currentStudent={this.state.currentStudent} refreshPost={this.refresh}></CommentForm>
                    </div>

                </div>
            </div>
        )
    }
}

class Posts extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            error: null,
            posts: [],
            next_url: "/api/posts/",
            count: null,
            more_exist: true,
        };
    }

    componentDidMount() {
        fetch("/api/current/")
            .then(res => res.json())
            .then(
                (result) => {
                    this.setState({currentStudent: result.student})
                },
                (error) => {
                    this.setState({
                        error
                    });
                }
            )
    }

    fetchData = () => {
        this.setState({more_exist: false})
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
                        return <Post post={post} key={post.id} currentStudent={this.state.currentStudent}/>
                    }.bind(this))
                }
            </div>
        </InfiniteScroll>
    }
}

export default Posts;
