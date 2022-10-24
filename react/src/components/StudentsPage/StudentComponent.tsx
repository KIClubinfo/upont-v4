import 'react';

interface Props {
    picture_url: string;
    student: {
        user: {
            first_name: string;
            last_name: string;
        }
        promo: {
            nickname: string;
        }
        department: string;
        profile_url: string;
    }
}

export const Student: React.FC<Props> = (props) => {
    return (
        <div className="col-xxl-2 col-xl-3 col-lg-4 col-sm-6">
            <div className="user-card">
                <div className="user-image">
                    <img className="image-centered" src={props.picture_url} alt=""></img>
                </div>
                <div className="user-information">
                    <span className="user-name">{props.student.user.first_name} {props.student.user.last_name}</span>
                    <span>{props.student.department} - Promo '{props.student.promo.nickname}</span>
                </div>
                <a href={props.student.profile_url} className="stretched-link"></a>
            </div>
        </div>
    )
}
