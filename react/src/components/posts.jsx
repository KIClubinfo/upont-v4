import React from 'react';
import InfiniteScroll from 'react-infinite-scroller';
import ReactMarkdown from 'react-markdown';
import gfm from 'remark-gfm';
import emoji from 'remark-emoji';
import {Comment} from './comment';
import {CommentForm} from './commentForm';


// auxilary functions
function addZero(i) {
    if (i < 10) {i = "0" + i}
    return i;
  }

/////////////////////////////

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
            <a className="news-card-header-name" href={state.post.author_url}>
                {state.post.club.name}
            </a>
        )
    }
    else {
        return (
            <a className="news-card-header-name" href={state.post.author_url}>
                {state.post.author.user.first_name} {state.post.author.user.last_name}
            </a>
        )
    }
}

function post_title(state) {
    return (
        <span className="news-card-header-title">{state.post.title}</span>
    )
}

function post_date(state) {
    const options = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' };
    var post_date = new Date(state.post.date);
    let post_hour = addZero(post_date.getHours());
    let post_minute = addZero(post_date.getMinutes());

        return (
            <span className="news-card-header-date">{post_date.toLocaleDateString("fr-FR", options)} - {post_hour}:{post_minute} </span>
        )
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


class Post extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            post: props.post,
            numberOfCommentsShown: 1,
        };
        this.refresh = this.refresh.bind(this);
        this.like = this.like.bind(this);
        this.post_like_button = this.post_like_button.bind(this);
        this.show_more = this.show_more.bind(this);
        this.show_less = this.show_less.bind(this);
        this.show_comments_button = this.show_comments_button.bind(this);
        this.edit_button = this.edit_button.bind(this);
    }

    refresh() {
        fetch(Urls["post_detail"](this.state.post.id))
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

    like(event) {
        event.preventDefault();
        let url;
        if (this.state.post.user_liked) {
            url = Urls["news:post_like"](this.state.post.id, "Dislike");
        }
        else {
            url = Urls["news:post_like"](this.state.post.id, "Like");
        }
        const csrfmiddlewaretoken = getCookie('csrftoken');
        const requestOptions = {
            method: 'POST',
            headers: {'Content-Type': 'text/html', 'X-CSRFToken': csrfmiddlewaretoken},
        };
        fetch(url, requestOptions)
            .then(this.setState({
            }))
            .then(response => console.log('Liked / Disliked successfully'))
            .catch(error => console.log('Submit error', error))
        setTimeout(() => this.refresh(), 200);
    }

    post_like_button() {
        if (this.state.post.user_liked) {
            return (
                <a onClick={this.like} className=""><i className="fas fa-heart" style={{ color: 'red' }}></i></a>
            )
        }
        else {
            return (
                <a onClick={this.like} className=""><i className="far fa-heart"></i></a>
            )
        }
    }

    show_more() {
        this.setState({numberOfCommentsShown: this.state.numberOfCommentsShown+5});
    }

    show_less() {
        this.setState({numberOfCommentsShown: 1});
    }

    show_comments_button() {
        if (this.state.post.comments.length <= 1){
            return <div></div>;
        }
        else if (this.state.numberOfCommentsShown < this.state.post.comments.length) {
            return <div style={{textAlign: "center"}}><a onClick={this.show_more}>Voir plus de commentaires</a></div>;
        }
        else {
            return <div style={{textAlign: "center"}}><a onClick={this.show_less}>Voir moins de commentaires</a></div>;
        }
    }

    edit_button() {
        if (this.state.post.can_edit) {
            return (
                <div className="news-card-header-edit-button">
                    <a href={this.state.post.edit_url}><i className="fas fa-edit"></i></a>
                </div>
            )
        }
    }
    
    show_event_button() {
        if (this.state.post.event_url) {
            return (
                <div className="centered-div">
                    <a href={this.state.post.event_url}><button class="button green-button">Voir l'événement</button></a>
                </div>
            )
        }
    }

    render() {
        return (
            <div>
                <div className="news-card" id={this.state.post.id}>
                    <div className="news-card-header">
                        {post_logo(this.state)}
                        <div className="news-card-header-text">
                            {post_author(this.state)}
                            {post_date(this.state)}
                        </div>
                        {this.edit_button()}
                    </div>
                    <div className="news-card-content">
                        <div className="news-card-content-title">
                            {post_title(this.state)}
                        </div>
                        <ReactMarkdown  remarkPlugins={[gfm,emoji]}>{this.state.post.content}</ReactMarkdown>
                        {this.show_event_button()}
                    </div>
                    {post_illustration(this.state)}
                    <div className="news-card-actions">
                        <span>{this.post_like_button()} {this.state.post.total_likes} </span>
                        &ensp;
                        <span><i className="fas fa-comment"></i> {this.state.post.total_comments}</span>
                    </div>
                    <div className="news-card-comments" style={{display: "block"}}>
                        {
                            this.state.post.comments.slice(0, this.state.numberOfCommentsShown).map(function f(comment) {
                                return <Comment comment={comment} key={comment.id} refreshPost={this.refresh}/>
                            }.bind(this))
                        }
                        {this.show_comments_button()}
                        <CommentForm post={this.state.post} currentStudent={this.props.currentStudent} refreshPost={this.refresh}></CommentForm>
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
            next_url: Urls["posts"](),
            count: null,
            more_exist: true,
            currentStudent: '',
        };
    }

    componentDidMount() {
        fetch(Urls["current_student"]())
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
                    else {
                        result.next = ""
                    }
                    this.setState({
                        next_url: "/" + result.next.replace(/^(?:\/\/|[^/]+)*\//, ''),
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
