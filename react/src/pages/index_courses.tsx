import { render } from 'react-dom';
import { Courses } from '../components/CoursesPage/CoursesComponent';

//@ts-ignore window.react_mount is declared in django template
render(<Courses />, window.react_mount);