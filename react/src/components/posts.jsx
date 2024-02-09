/* eslint-disable no-script-url */
/* eslint-disable react/jsx-no-script-url */
/* eslint-disable jsx-a11y/anchor-is-valid */
/* eslint-disable max-classes-per-file */
/* eslint-disable react/prop-types */
import React from 'react';
import InfiniteScroll from 'react-infinite-scroller';
import ReactMarkdown from 'react-markdown';
import gfm from 'remark-gfm';
import emoji from 'remark-emoji';
import Comment from './comment';
import CommentForm from './commentForm';
import { addZero } from './utils/utils';
import { getCookie } from './utils/csrf';
import Resource from './resource';
import YouTube from 'react-youtube';

function postLogo(state) {
  if (state.post.club) {
    return (
      <div className="news-card-header-image">
        <img className="image-centered" src={state.post.club.logo_url} alt="" />
      </div>
    );
  }
  return (
    <div className="news-card-header-image">
      <img
        className="image-centered"
        src={state.post.author.picture_url}
        alt=""
      />
    </div>
  );
}

function postAuthor(state) {
  if (state.post.club) {
    return (
      <a className="news-card-header-name" href={state.post.author_url}>
        {state.post.club.name}
      </a>
    );
  }
  return (
    <a className="news-card-header-name" href={state.post.author_url}>
      {state.post.author.user.first_name} {state.post.author.user.last_name}
    </a>
  );
}

function postTitle(state) {
  return <span className="news-card-header-title">{state.post.title}</span>;
}

function postDate(state) {
  const options = {
    weekday: 'short',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  };
  const date = new Date(state.post.date);
  const hour = addZero(date.getHours());
  const minute = addZero(date.getMinutes());

  return (
    <span className="news-card-header-date">
      {date.toLocaleDateString('fr-FR', options)} - {hour}:{minute}{' '}
    </span>
  );
}

function postClubAuthor(state) {
  if (state.post.club && state.post.can_edit) {
    return (
      <span className="news-card-header-date">
        Posté par&nbsp;
        <a href={state.post.user_author_url}>
          {state.post.author.user.first_name} {state.post.author.user.last_name}
        </a>
      </span>
    );
  }

  return null;
}

function postIllustration(state) {
  const temp = [];
  for (const index in state.post.resources) {
    if (state.post.resources[index].type === 'image') {
      temp.push(
        <div className="news-card-images">
          <div className="news-card-carousel">
            <div className="carousel-cell">
              <img
                className="news-card_image_sized"
                src={state.post.resources[index].url}
                alt=""
              />
            </div>
          </div>
        </div>,
      );
    } else if (state.post.resources[index].type === 'video') {
      var id = '';
      var url = state.post.resources[index].url;
      url = url
        .replace(/(>|<)/gi, '')
        .split(/(vi\/|v=|\/v\/|youtu\.be\/|\/embed\/)/);
      if (url[2] !== undefined) {
        id = url[2].split(/[^0-9a-z_\-]/i);
        id = id[0];
      } else {
        id = url;
      }
      temp.push(
        <div className="news-card-images">
          <div className="news-card-carousel">
            <div className="carousel-cell">
              <YouTube videoId={id} />
            </div>
          </div>
        </div>,
      );
    }
  }

  return temp;
}

class Post extends React.Component {
  constructor(props) {
    super(props);
    const { mode } = props;
    this.state = {
      post: props.post,
      mode,
      numberOfCommentsShown: 1,
    };
    this.refresh = this.refresh.bind(this);
    this.like = this.like.bind(this);
    this.dislike = this.dislike.bind(this);
    this.post_like_button = this.post_like_button.bind(this);
    this.post_dislike_button = this.post_dislike_button.bind(this);
    this.post_bookmark_button = this.post_bookmark_button.bind(this);
    this.bookmark = this.bookmark.bind(this);
    this.show_more = this.show_more.bind(this);
    this.show_less = this.show_less.bind(this);
    this.show_comments_button = this.show_comments_button.bind(this);
    this.edit_button = this.edit_button.bind(this);
    this.delete_post = this.delete_post.bind(this);
  }

  refresh() {
    // eslint-disable-next-line no-undef
    fetch(Urls.post_detail(this.state.post.id))
      .then((res) => res.json())
      .then(
        (result) => {
          this.setState({ post: result });
        },
        (error) => {
          this.setState({
            error,
          });
        },
      );
  }

  like(event) {
    event.preventDefault();
    let url;
    if (this.state.post.user_liked) {
      // eslint-disable-next-line no-undef
      url = Urls['news:post_like'](this.state.post.id, 'Unlike');
    } else {
      // eslint-disable-next-line no-undef
      url = Urls['news:post_like'](this.state.post.id, 'Like');
    }
    const csrfmiddlewaretoken = getCookie('csrftoken');
    const requestOptions = {
      method: 'POST',
      headers: {
        'Content-Type': 'text/html',
        'X-CSRFToken': csrfmiddlewaretoken,
      },
    };
    fetch(url, requestOptions)
      .then(this.setState({}))
      // eslint-disable-next-line no-console
      .then(() => console.log('Liked / Unliked successfully'))
      // eslint-disable-next-line no-console
      .catch((error) => console.log('Submit error', error));
    setTimeout(() => this.refresh(), 200);
  }

  dislike(event) {
    event.preventDefault();
    let url;
    if (this.state.post.user_disliked) {
      // eslint-disable-next-line no-undef
      url = Urls['news:post_like'](this.state.post.id, 'Undislike');
    } else {
      // eslint-disable-next-line no-undef
      url = Urls['news:post_like'](this.state.post.id, 'Dislike');
    }
    const csrfmiddlewaretoken = getCookie('csrftoken');
    const requestOptions = {
      method: 'POST',
      headers: {
        'Content-Type': 'text/html',
        'X-CSRFToken': csrfmiddlewaretoken,
      },
    };
    fetch(url, requestOptions)
      .then(this.setState({}))
      // eslint-disable-next-line no-console
      .then(() => console.log('Disliked / Undisliked successfully'))
      // eslint-disable-next-line no-console
      .catch((error) => console.log('Submit error', error));
    setTimeout(() => this.refresh(), 200);
  }

  post_like_button() {
    if (this.state.post.user_liked) {
      return (
        <switch onClick={this.like} className="">
          <i className="fas fa-arrow-up" style={{ color: '#F33D3D' }} />
        </switch>
      );
    }
    return (
      <switch onClick={this.like} className="">
        <i className="fas fa-arrow-up" />
      </switch>
    );
  }

  post_dislike_button() {
    if (this.state.post.user_disliked) {
      return (
        <switch onClick={this.dislike} className="">
          <i className="fas fa-arrow-down" style={{ color: '#3DC1F3' }} />
        </switch>
      );
    }
    return (
      <switch onClick={this.dislike} className="">
        <i className="fas fa-arrow-down" />
      </switch>
    );
  }

  post_bookmark_button() {
    if (this.state.post.user_bookmarked) {
      return (
        <switch onClick={this.bookmark} className="">
          <i className="fas fa-bookmark" style={{ color: '#3DC1F3' }} />
        </switch>
      );
    }
    return (
      <switch onClick={this.bookmark} className="">
        <i className="fas fa-bookmark" style={{ color: '#575555' }} />
      </switch>
    );
  }

  bookmark(event) {
    event.preventDefault();
    let url;
    if (this.state.post.user_bookmarked) {
      // eslint-disable-next-line no-undef
      url = Urls['news:post_like'](this.state.post.id, 'Unbookmark');
    } else {
      // eslint-disable-next-line no-undef
      url = Urls['news:post_like'](this.state.post.id, 'Bookmark');
    }
    const csrfmiddlewaretoken = getCookie('csrftoken');
    const requestOptions = {
      method: 'POST',
      headers: {
        'Content-Type': 'text/html',
        'X-CSRFToken': csrfmiddlewaretoken,
      },
    };
    fetch(url, requestOptions)
      .then(this.setState({}))
      // eslint-disable-next-line no-console
      .then(() => console.log('Bookmarked / Unbookmarked successfully'))
      // eslint-disable-next-line no-console
      .catch((error) => console.log('Submit error', error));
    setTimeout(() => this.refresh(), 200);
  }

  show_more() {
    this.setState((prevState) => ({
      numberOfCommentsShown: prevState.numberOfCommentsShown + 5,
    }));
  }

  show_less() {
    this.setState({ numberOfCommentsShown: 1 });
  }

  delete_post(event) {
    event.preventDefault();
    // eslint-disable-next-line no-undef
    const url = Urls.api_news_post_delete();
    const csrfmiddlewaretoken = getCookie('csrftoken');
    const requestOptions = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfmiddlewaretoken,
      },
      body: JSON.stringify({ post: this.state.post.id }),
    };
    fetch(url, requestOptions)
      .then(this.setState({}))
      // eslint-disable-next-line no-console
      .then(() => console.log('Successfully deleted post'))
      // eslint-disable-next-line no-console
      .catch((error) => console.log('Submit error', error));
    window.location.reload();
  }

  show_comments_button() {
    if (this.state.post.comments.length <= 1) {
      return <div />;
    }
    if (this.state.numberOfCommentsShown < this.state.post.comments.length) {
      return (
        <div
          className="news-card-edit-comment-container"
          style={{ textAlign: 'center' }}
        >
          <a href="javascript:void(0)" onClick={this.show_more}>
            Voir plus de commentaires
          </a>
        </div>
      );
    }
    return (
      <div
        className="news-card-edit-comment-container"
        style={{ textAlign: 'center' }}
      >
        <a href="javascript:void(0)" onClick={this.show_less}>
          Voir moins de commentaires
        </a>
      </div>
    );
  }

  edit_button() {
    if (this.state.post.can_edit) {
      return (
        <div className="news-card-header-edit-button">
          <a href={this.state.post.edit_url}>
            <i className="fas fa-edit" />
          </a>
        </div>
      );
    }
    if (this.state.post.can_moderate) {
      return (
        <div className="news-card-header-edit-button">
          <a href="javascript:void(0)" onClick={this.delete_post}>
            <i className="fa fa-gavel" />
          </a>
        </div>
      );
    }

    return null;
  }

  show_event_button() {
    if (this.state.post.event_url) {
      return (
        <div className="centered-div">
          <a href={this.state.post.event_url}>
            <button className="button green-button" type="button">
              Voir l'événement
            </button>
          </a>
        </div>
      );
    }

    return null;
  }

  show_event_name() {
    if (this.state.post.event_url) {
      return (
        <p>
          <i className="fas fa-calendar-alt" /> Ce post est associé à
          l'événement{' '}
          <a href={this.state.post.event_url}>{this.state.post.event_name}</a>
        </p>
      );
    }

    return null;
  }

  render() {
    return (
      <div>
        <div className="news-card" id={this.state.post.id}>
          <div className="news-card-header">
            {postLogo(this.state)}
            <div className="news-card-header-text">
              {postAuthor(this.state)}
              {postClubAuthor(this.state)}
              {postDate(this.state)}
            </div>
            {this.edit_button()}
          </div>
          <div className="news-card-content">
            {this.show_event_name()}
            <div className="news-card-content-title">
              {postTitle(this.state)}
            </div>
            <ReactMarkdown remarkPlugins={[gfm, emoji]}>
              {this.state.post.content}
            </ReactMarkdown>
            {this.show_event_button()}
          </div>
          {postIllustration(this.state)}
          {this.state.post.resource.map((resource) => (
            <Resource resource={resource} key={resource.id} />
          ))}
          <div className="news-card-actions">
            <span>
              {this.post_like_button()} {this.state.post.total_likes}{' '}
            </span>
            &ensp;
            <span>
              {this.post_dislike_button()} {this.state.post.total_dislikes}{' '}
            </span>
            &ensp;
            <span>
              <i className="fas fa-comment" /> {this.state.post.total_comments}
            </span>
            &ensp;
            <span>{this.post_bookmark_button()}</span>
          </div>
          <div style={{ display: 'block' }}>
            {this.state.post.comments
              .slice(0, this.state.numberOfCommentsShown)
              .map((comment) => (
                <Comment
                  comment={comment}
                  key={comment.id}
                  refreshPost={this.refresh}
                />
              ))}
            {this.show_comments_button()}
            <CommentForm
              post_id={this.state.post.id}
              currentStudent={this.props.currentStudent}
              refreshPost={this.refresh}
              mode={this.state.mode}
            />
          </div>
        </div>
      </div>
    );
  }
}

class Posts extends React.Component {
  constructor(props) {
    super(props);
    const { mode, bookmark } = props;
    let url;
    if (mode === 'social') {
      // eslint-disable-next-line no-undef
      if (bookmark === 'true') {
        // eslint-disable-next-line no-undef
        url = `${Urls.postList()}?mode=social&bookmark=true`;
      } else {
        // eslint-disable-next-line no-undef
        url = `${Urls.postList()}?mode=social`;
      }
    } else if (mode === 'course') {
      const { courseId } = props;
      // eslint-disable-next-line no-undef
      url = `${Urls.postList()}?mode=course&course_id=${courseId}`;
    }
    this.state = {
      mode,
      posts: [],
      next_url: url,
      more_exist: true,
      currentStudent: '',
    };
  }

  componentDidMount() {
    // eslint-disable-next-line no-undef
    fetch(Urls.current_student())
      .then((res) => res.json())
      .then(
        (result) => {
          this.setState({ currentStudent: result.student });
        },
        (error) => {
          // eslint-disable-next-line no-console
          console.error(error);
        },
      );
  }

  fetchData = () => {
    this.setState({ more_exist: false });
    fetch(this.state.next_url)
      .then((res) => res.json())
      .then(
        (result) => {
          let { next } = result;
          let hasMore = false;
          if (next) {
            hasMore = true;
          } else {
            next = '';
          }
          this.setState((prevState) => ({
            next_url: `/${next.replace(/^(?:\/\/|[^/]+)*\//, '')}`,
            posts: prevState.posts.concat(result.results),
            more_exist: hasMore,
          }));
        },
        (error) => {
          // eslint-disable-next-line no-console
          console.log(error);
        },
      );
  };

  render() {
    return (
      <InfiniteScroll
        loadMore={this.fetchData}
        hasMore={this.state.more_exist}
        loader={
          <div key="-1" style={{ textAlign: 'center', marginTop: '10%' }}>
            <i className="fa fa-lg fa-spinner fa-spin" />
          </div>
        }
      >
        <div className="row" key="-2">
          {this.state.posts.map((post) => (
            <Post
              post={post}
              key={post.id}
              currentStudent={this.state.currentStudent}
              mode={this.state.mode}
            />
          ))}
        </div>
      </InfiniteScroll>
    );
  }
}

export default Posts;
