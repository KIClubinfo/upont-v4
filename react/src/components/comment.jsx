import React from 'react';
import PropTypes from 'prop-types';
import { addZero } from './utils/utils';

function commentLogo(state) {
  if (state.comment.club) {
    return (
      <div className="news-card-comment-user-pic">
        <img
          className="image-centered"
          src={state.comment.club.logo_url}
          alt=""
        />
      </div>
    );
  }
  return (
    <div className="news-card-comment-user-pic">
      <img
        className="image-centered"
        src={state.comment.author.picture_url}
        alt=""
      />
    </div>
  );
}

function commentContent(state) {
  const options = {
    weekday: 'short',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  };
  const commentDate = new Date(state.comment.date);
  const commentHour = addZero(commentDate.getHours());
  const commentMinute = addZero(commentDate.getMinutes());
  if (state.comment.club && state.comment.is_my_comment) {
    return (
      <div className="news-card-comment-box">
        <a className="text-bold" href={state.comment.author_url}>
          {state.comment.club.name}
        </a>
        <br />
        <span className="news-card-header-date">
          Posté par&nbsp;
          <a href={state.comment.user_author_url}>
            {state.comment.author.user.first_name}{' '}
            {state.comment.author.user.last_name}
          </a>
        </span>
        <br />
        <span className="news-card-header-date">
          {commentDate.toLocaleDateString('fr-FR', options)} - {commentHour}:
          {commentMinute}
        </span>
        <br />
        <br />
        {state.comment.content}
      </div>
    );
  }
  if (state.comment.club) {
    return (
      <div className="news-card-comment-box">
        <a className="text-bold" href={state.comment.author_url}>
          {state.comment.club.name}
        </a>
        <br />
        <span className="news-card-header-date">
          {commentDate.toLocaleDateString('fr-FR', options)} - {commentHour}:
          {commentMinute}
        </span>
        <br />
        <br />
        {state.comment.content}
      </div>
    );
  }
  return (
    <div className="news-card-comment-box">
      <a className="text-bold" href={state.comment.author_url}>
        {state.comment.author.user.first_name}{' '}
        {state.comment.author.user.last_name}
      </a>
      <br />
      <span className="news-card-header-date">
        {commentDate.toLocaleDateString('fr-FR', options)} - {commentHour}:
        {commentMinute}
      </span>
      <br />
      <br />
      {state.comment.content}
    </div>
  );
}

export default class Comment extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      comment: props.comment,
    };
    this.delete = this.delete.bind(this);
    this.moderate = this.moderate.bind(this);
    // this.comment_delete_button = this.commentDeleteButton.bind(this);
  }

  delete(event) {
    event.preventDefault();
    // eslint-disable-next-line no-undef
    const url = Urls['news:comment_delete'](this.state.comment.id);
    // eslint-disable-next-line no-undef
    const csrfmiddlewaretoken = getCookie('csrftoken');
    const requestOptions = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfmiddlewaretoken,
      },
      body: JSON.stringify({ comment_id: this.state.comment.id }),
    };
    fetch(url, requestOptions)
      .then(this.setState({}))
      // eslint-disable-next-line no-console
      .then(() => console.log('Deleted successfully'))
      // eslint-disable-next-line no-console
      .catch((error) => console.log('Submit error', error));
    setTimeout(() => this.props.refreshPost(), 200);
  }

  moderate(event) {
    event.preventDefault();
    // eslint-disable-next-line no-undef
    const url = Urls.api_news_comment_delete();
    // eslint-disable-next-line no-undef
    const csrfmiddlewaretoken = getCookie('csrftoken');
    const requestOptions = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfmiddlewaretoken,
      },
      body: JSON.stringify({ comment: this.state.comment.id }),
    };
    fetch(url, requestOptions)
      .then(this.setState({}))
      // eslint-disable-next-line no-console
      .then(() => console.log('Deleted successfully'))
      // eslint-disable-next-line no-console
      .catch((error) => console.log('Submit error', error));
    setTimeout(() => this.props.refreshPost(), 200);
  }

  commentDeleteButton() {
    if (this.state.comment.is_my_comment) {
      return (
        // eslint-disable-next-line jsx-a11y/anchor-is-valid, jsx-a11y/click-events-have-key-events, jsx-a11y/no-static-element-interactions
        <a onClick={this.delete}>
          <i className="fas fa-times-circle" />
        </a>
      );
    }
    if (this.state.comment.can_moderate) {
      return (
        // eslint-disable-next-line
        <a href="javascript:void(0)" onClick={this.moderate}>
          <i className="fas fa-times-circle" />
        </a>
      );
    }

    return null;
  }

  render() {
    return (
      <div className="news-card-comments">
        <div className="news-card-comment">
          {commentLogo(this.state)}
          {commentContent(this.state)}
          {this.commentDeleteButton()}
        </div>
      </div>
    );
  }
}
Comment.propTypes = {
  comment: PropTypes.shape({
    id: PropTypes.number,
    is_my_comment: PropTypes.bool,
  }).isRequired,
  refreshPost: PropTypes.func.isRequired,
};
