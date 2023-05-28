query_dict =    {
                "projects"              :   """
                                            SELECT
                                                projects.project_id AS `ID проекта`,
                                                projects.project_name AS `Название проекта`,
                                                projects.project_description AS `Описание`,
                                                projects.project_result AS `Результат`,
                                                projects.project_start_date AS `Дата начала`,
                                                projects.project_end_date AS `Дата окончания`,
                                                CASE
                                                    WHEN YEAR(projects.project_start_date) = 0
                                                        THEN NULL
                                                    WHEN MONTH(projects.project_start_date) > 8
                                                        THEN CONCAT_WS(' - ', YEAR(projects.project_start_date), YEAR(projects.project_start_date)+1)
                                                    ELSE CONCAT_WS(' - ', YEAR(projects.project_start_date)-1, YEAR(projects.project_start_date))
                                                END AS `Академический год`,
                                                projects.project_company_id AS `ID компании`,
                                                companies.company_name AS `Название компании`,
                                                company_types.company_type AS `Тип компании`,
                                                company_spheres.company_sphere AS `Отрасль`,
                                                project_grades.grade AS `Грейд`,
                                                project_fields.field AS `Микро-направление`,
                                                field_spheres.sphere AS `Макро-направление`,
                                                CASE
                                                    WHEN projects.is_frozen = 1
                                                    THEN 'Заморожен'
                                                    WHEN projects.is_frozen <> 1 AND (DAYNAME(projects.project_end_date) IS NULL OR DATE(projects.project_end_date) >= CURDATE())
                                                    THEN 'Активен' ELSE 'Завершен'
                                                END AS Статус,
                                                IFNULL(T0.Участников, 0) AS `Кол-во участников`
                                            FROM projects
                                            LEFT JOIN project_grades
                                                ON projects.project_grade_id = project_grades.grade_id
                                            LEFT JOIN project_fields
                                                ON projects.project_field_id = project_fields.field_id
                                            LEFT JOIN field_spheres
                                                ON project_fields.sphere_id = field_spheres.sphere_id
                                            LEFT JOIN companies
                                                ON projects.project_company_id = companies.company_id
                                            LEFT JOIN company_spheres
                                                ON companies.company_sphere_id = company_spheres.company_sphere_id
                                            LEFT JOIN company_types
                                                ON companies.company_type_id = company_types.company_type_id
                                            LEFT JOIN (
                                                (SELECT students_in_projects.project_id, COUNT(students_in_projects.project_id) AS Участников FROM students_in_projects GROUP BY students_in_projects.project_id)) AS T0
                                                ON projects.project_id = T0.project_id;
                                            """,
                "events"                :   """
                                            SELECT
                                                events.event_id AS `ID мероприятия`,
                                                events.event_name AS Название,
                                                events.event_start_date AS `Дата начала`,
                                                events.event_end_date AS `Дата окончания`,
                                                events.event_description AS Описание,
                                                regions.region AS Регион,
                                                CASE
                                                    WHEN events.is_frozen = 1
                                                    THEN 'Заморожен'
                                                    WHEN events.is_frozen <> 1 AND (DAYNAME(events.event_end_date) IS NULL OR DATE(events.event_end_date) >= CURDATE())
                                                    THEN 'Активен' ELSE 'Завершен'
                                                END AS Статус,
                                                IFNULL(T0.Участников, 0) AS `Кол-во участников`
                                            FROM events
                                            INNER JOIN regions
                                                ON events.event_region_id = regions.region_id
                                            LEFT JOIN (
                                                (SELECT participants_in_events.event_id, COUNT(participants_in_events.event_id) AS Участников FROM participants_in_events GROUP BY participants_in_events.event_id)) AS T0
                                                ON events.event_id = T0.event_id;
                                            """,

                "students"              :   """
                                            SELECT
                                                students.student_id AS 'ID студента',
                                                CONCAT_WS(
                                                ' ',
                                                students.student_surname,
                                                students.student_name,
                                                students.student_midname) AS 'ФИО студента',
                                                CASE 
                                                    WHEN (students.masters_start_year = 0 OR students.masters_start_year IS NULL OR CURDATE() < DATE_FORMAT(CONCAT(students.masters_start_year, '-09-01'), '%d.%m.%Y'))
                                                    THEN
                                                    CASE 
                                                        WHEN STR_TO_DATE(CONCAT(students.bachelors_start_year, '-09-01'), '%Y-%m-%d') <= CURDATE() AND CURDATE() < STR_TO_DATE(CONCAT(students.bachelors_start_year+1, '-09-01'), '%Y-%m-%d')  
                                                        THEN 1
                                                        WHEN STR_TO_DATE(CONCAT(students.bachelors_start_year+1, '-09-01'), '%Y-%m-%d') <= CURDATE() AND CURDATE() < STR_TO_DATE(CONCAT(students.bachelors_start_year+2, '-09-01'), '%Y-%m-%d')
                                                        THEN 2
                                                        WHEN STR_TO_DATE(CONCAT(students.bachelors_start_year+2, '-09-01'), '%Y-%m-%d') <= CURDATE() AND CURDATE() < STR_TO_DATE(CONCAT(students.bachelors_start_year+3, '-09-01'), '%Y-%m-%d')
                                                        THEN 3
                                                        WHEN STR_TO_DATE(CONCAT(students.bachelors_start_year+3, '-09-01'), '%Y-%m-%d') <= CURDATE() AND CURDATE() < STR_TO_DATE(CONCAT(students.bachelors_start_year+4, '-09-01'), '%Y-%m-%d')
                                                        THEN 4 
                                                    ELSE 'Выпуск'
                                                    END 
                                                    ELSE 
                                                    CASE  
                                                        WHEN STR_TO_DATE(CONCAT(students.masters_start_year, '-09-01'), '%Y-%m-%d') <= CURDATE() AND CURDATE() < STR_TO_DATE(CONCAT(students.masters_start_year+1, '-09-01'), '%Y-%m-%d')
                                                        THEN 1
                                                        WHEN STR_TO_DATE(CONCAT(students.masters_start_year+1, '-09-01'), '%Y-%m-%d') <= CURDATE() AND CURDATE() < STR_TO_DATE(CONCAT(students.masters_start_year+2, '-09-01'), '%Y-%m-%d')
                                                        THEN 2
                                                    ELSE 'Выпуск'
                                                    END
                                                END AS 'Курс',
                                                CASE 
                                                    WHEN (students.masters_start_year = 0 OR students.masters_start_year IS NULL OR CURDATE() < DATE_FORMAT(CONCAT(students.masters_start_year, '-09-01'), '%d.%m.%Y'))
                                                    THEN 'Бакалавриат'
                                                    ELSE 'Магистратура'
                                                END AS 'Программа',
                                                CASE 
                                                    WHEN (students.masters_start_year = 0 OR students.masters_start_year IS NULL OR CURDATE() < DATE_FORMAT(CONCAT(students.masters_start_year, '-09-01'), '%d.%m.%Y'))
                                                    THEN CONCAT(students.bachelors_start_year, ' - ', students.bachelors_start_year+4)
                                                    ELSE CONCAT(students.masters_start_year, ' - ', students.masters_start_year+2)
                                                END AS 'Поток',
                                                CASE 
                                                    WHEN (students.masters_start_year = 0 OR students.masters_start_year IS NULL OR CURDATE() < DATE_FORMAT(CONCAT(students.masters_start_year, '-09-01'), '%d.%m.%Y'))
                                                    THEN bach_name
                                                    ELSE mast_name
                                                END AS 'ВУЗ',
                                                CASE 
                                                    WHEN (students.masters_start_year = 0 OR students.masters_start_year IS NULL OR CURDATE() < DATE_FORMAT(CONCAT(students.masters_start_year, '-09-01'), '%d.%m.%Y'))
                                                    THEN bach_reg_name
                                                    ELSE mast_reg_name
                                                END AS 'Регион',
                                                CASE
                                                    WHEN students.student_id in (SELECT students_in_projects.student_id FROM students_in_projects WHERE students_in_projects.is_moderator = 1)
                                                    THEN 1
                                                    ELSE 0
                                                END AS 'Опыт модератора',
                                                CASE
                                                    WHEN students.student_id in (SELECT students_in_projects.student_id FROM students_in_projects WHERE students_in_projects.is_curator = 1)
                                                    THEN 1
                                                    ELSE 0
                                                END AS 'Опыт куратора',
                                                students.is_banned AS 'Отстранен'
                                            FROM students
                                            LEFT JOIN universities
                                                ON students.bachelors_university_id = universities.university_id
                                            LEFT JOIN   (
                                                            (SELECT universities.university_id AS 'bach_id', universities.university_name AS 'bach_name', universities.university_region_id AS 'bach_reg_id' FROM universities) AS T0
                                                                LEFT JOIN
                                                                    (SELECT regions.region_id, regions.region 'bach_reg_name', regions.is_foreign FROM regions) AS T1
                                                                    ON bach_reg_id = T1.region_id
                                                        )
                                                ON bach_id = students.bachelors_university_id
                                            LEFT JOIN   (
                                                            (SELECT universities.university_id AS 'mast_id', universities.university_name AS 'mast_name', universities.university_region_id AS 'mast_reg_id' FROM universities) AS T2
                                                                LEFT JOIN
                                                                    (SELECT regions.region_id, regions.region AS 'mast_reg_name', regions.is_foreign FROM regions) AS T3
                                                                    ON mast_reg_id = T3.region_id
                                                        )
                                                ON mast_id = students.masters_university_id;
                                            """,

                "teachers"              :   """
                                            SELECT
                                                T0.teacher_id AS 'ID преподавателя',
                                                CONCAT_WS(
                                                    ' ',
                                                    T0.teacher_surname,
                                                    T0.teacher_name,
                                                    T0.teacher_midname) AS 'ФИО преподавателя'
                                            FROM (SELECT teachers.teacher_id, teachers.teacher_surname, teachers.teacher_name, teachers.teacher_midname FROM teachers) AS T0;
                                            """,

                "universities"          :   """
                                            SELECT
                                            universities.university_id AS 'ID вуза',
                                            universities.university_name AS 'Название вуза',
                                            T0.region AS 'Регион'
                                            FROM universities
                                            LEFT JOIN   (SELECT regions.region_id, regions.region FROM regions) AS T0
                                                ON universities.university_id = T0.region_id;
                                            """,
                                            
                "teachers_in_projects"  :   """
                                            SELECT
                                                teachers_in_projects.project_id AS 'ID проекта',
                                                CONCAT_WS(
                                                    ' ',
                                                    teachers.teacher_surname,
                                                    teachers.teacher_name,
                                                    teachers.teacher_midname) AS 'ФИО преподавателя',
                                                teachers_in_projects.teacher_id AS 'ID преподавателя'
                                            FROM teachers_in_projects
                                            LEFT JOIN
                                                teachers ON teachers_in_projects.teacher_id = teachers.teacher_id;
                                            """,

                "teachers_in_events"    :   """
                                            SELECT
                                                teachers_in_events.event_id AS 'ID мероприятия',
                                                CONCAT_WS(
                                                    ' ',
                                                    teachers.teacher_surname,
                                                    teachers.teacher_name,
                                                    teachers.teacher_midname) AS 'ФИО преподавателя',
                                                teachers_in_events.teacher_id AS 'ID преподавателя'
                                            FROM teachers_in_events
                                            LEFT JOIN
                                                teachers ON teachers_in_events.teacher_id = teachers.teacher_id;
                                            """,
                
                "companies"             :   """
                                            SELECT
                                                T1.company_id AS 'ID компании',
                                                T1.company_name AS 'Название компании',
                                                T2.company_type AS 'Тип компании',
                                                T3.company_sphere AS 'Отрасль',
                                                T1.company_website AS 'Веб-сайт',
                                                T1.company_logo AS 'Логотип'
                                            FROM    (
                                                        (SELECT companies.company_id, companies.company_name, companies.company_type_id, companies.company_sphere_id, companies.company_website, companies.company_logo FROM companies) AS T1
                                                            LEFT JOIN 
                                                                (SELECT company_types.company_type_id, company_types.company_type FROM company_types) AS T2
                                                                ON T1.company_type_id = T2.company_type_id
                                                            LEFT JOIN
                                                                (SELECT company_spheres.company_sphere_id, company_spheres.company_sphere FROM company_spheres) AS T3
                                                                ON T1.company_sphere_id = T3.company_sphere_id
                                                    );
                                            """,
                                            
                "project_fields"        :   """
                                            SELECT
                                                field_spheres.sphere AS 'Макро',
                                                project_fields.field AS 'Микро'                                                
                                            FROM project_fields
                                            LEFT JOIN
                                                field_spheres ON project_fields.sphere_id   = field_spheres.sphere_id;
                                            """,

                "students_in_events"    :   """
                                            SELECT

                                                students.student_id AS `ID студента`,
                                                events.event_id AS `ID мероприятия`,
                                                regions.region AS Регион,
                                                events.event_start_date AS `Дата начала мероприятия`,
                                                events.event_end_date AS `Дата окончания мероприятия`,
                                                CONCAT_WS(
                                                    ' ',
                                                    students.student_surname,
                                                    students.student_name,
                                                    students.student_midname)
                                                AS 'ФИО студента',
                                                participants_in_events.is_manager AS Модератор,
                                                CASE WHEN students.masters_start_year = 0 OR
                                                    students.masters_start_year IS NULL OR
                                                    events.event_start_date < STR_TO_DATE(CONCAT(students.masters_start_year, '-09-01'), '%Y-%m-%d') THEN CASE WHEN STR_TO_DATE(CONCAT(students.bachelors_start_year, '-09-01'), '%Y-%m-%d') <= events.event_start_date AND
                                                            events.event_start_date < STR_TO_DATE(CONCAT(students.bachelors_start_year + 1, '-09-01'), '%Y-%m-%d') THEN '1' WHEN STR_TO_DATE(CONCAT(students.bachelors_start_year + 1, '-09-01'), '%Y-%m-%d') <= events.event_start_date AND
                                                            events.event_start_date < STR_TO_DATE(CONCAT(students.bachelors_start_year + 2, '-09-01'), '%Y-%m-%d') THEN '2' WHEN STR_TO_DATE(CONCAT(students.bachelors_start_year + 2, '-09-01'), '%Y-%m-%d') <= events.event_start_date AND
                                                            events.event_start_date < STR_TO_DATE(CONCAT(students.bachelors_start_year + 3, '-09-01'), '%Y-%m-%d') THEN '3' WHEN STR_TO_DATE(CONCAT(students.bachelors_start_year + 3, '-09-01'), '%Y-%m-%d') <= events.event_start_date AND
                                                            events.event_start_date < STR_TO_DATE(CONCAT(students.bachelors_start_year + 4, '-09-01'), '%Y-%m-%d') THEN '4' ELSE NULL END ELSE CASE WHEN STR_TO_DATE(CONCAT(students.masters_start_year, '-09-01'), '%Y-%m-%d') <= events.event_start_date AND
                                                        events.event_start_date < STR_TO_DATE(CONCAT(students.masters_start_year + 1, '-09-01'), '%Y-%m-%d') THEN '1' WHEN STR_TO_DATE(CONCAT(students.masters_start_year + 1, '-09-01'), '%Y-%m-%d') <= events.event_start_date AND
                                                        events.event_start_date < STR_TO_DATE(CONCAT(students.masters_start_year + 2, '-09-01'), '%Y-%m-%d') THEN '2' ELSE NULL END END AS 'Курс в моменте',
                                                CASE WHEN students.masters_start_year = 0 OR
                                                    students.masters_start_year IS NULL OR
                                                    events.event_start_date < STR_TO_DATE(CONCAT(students.masters_start_year, '-09-01'), '%Y-%m-%d') THEN 'Бакалавриат' ELSE 'Магистратура' END AS 'Программа в моменте',
                                                CASE WHEN students.masters_start_year = 0 OR
                                                    students.masters_start_year IS NULL OR
                                                    events.event_start_date < STR_TO_DATE(CONCAT(students.masters_start_year, '-09-01'), '%Y-%m-%d') THEN Бакалавры.university_name ELSE Магистры.university_name END AS 'ВУЗ в моменте',
                                                CASE
                                                        WHEN YEAR(events.event_start_date) = 0
                                                            THEN NULL
                                                        WHEN MONTH(events.event_start_date) > 8
                                                            THEN CONCAT_WS(' - ', YEAR(events.event_start_date), YEAR(events.event_start_date)+1)
                                                        ELSE CONCAT_WS(' - ', YEAR(events.event_start_date)-1, YEAR(events.event_start_date))
                                                    END AS `Академический год`
                                            FROM participants_in_events
                                            LEFT OUTER JOIN events
                                                ON participants_in_events.event_id = events.event_id
                                            LEFT OUTER JOIN students
                                                ON participants_in_events.student_id = students.student_id
                                            LEFT OUTER JOIN regions
                                                ON events.event_region_id = regions.region_id
                                            LEFT OUTER JOIN (SELECT
                                                students.student_id,
                                                universities.university_name,
                                                regions.region
                                                FROM students
                                                INNER JOIN universities
                                                    ON students.bachelors_university_id = universities.university_id
                                                INNER JOIN regions
                                                    ON universities.university_region_id = regions.region_id) Бакалавры
                                                ON students.student_id = Бакалавры.student_id
                                            LEFT OUTER JOIN (SELECT
                                                students.student_id,
                                                universities.university_name,
                                                regions.region
                                                FROM students
                                                INNER JOIN universities
                                                    ON students.masters_university_id = universities.university_id
                                                INNER JOIN regions
                                                    ON universities.university_region_id = regions.region_id) Магистры
                                                ON students.student_id = Магистры.student_id;
                                            """,
                "students_in_projects"  :   """
                                            SELECT
                                            projects.project_id AS `ID проекта`,
                                            CASE
                                                WHEN projects.is_frozen = 1
                                                THEN 'Заморожен'
                                                WHEN projects.is_frozen <> 1 AND (DAYNAME(projects.project_end_date) IS NULL OR DATE(projects.project_end_date) >= CURDATE())
                                                THEN 'Активен' ELSE 'Завершен'
                                            END AS Статус,
                                            students.student_id AS `ID студента`,
                                            CONCAT_WS(
                                                ' ',
                                                students.student_surname,
                                                students.student_name,
                                                students.student_midname)
                                            AS 'ФИО студента',
                                            students_in_projects.team AS Команда,
                                            students_in_projects.is_curator AS Куратор,
                                            students_in_projects.is_moderator AS Модератор,
                                            CASE WHEN students.masters_start_year = 0 OR
                                                students.masters_start_year IS NULL OR
                                                projects.project_start_date < STR_TO_DATE(CONCAT(students.masters_start_year, '-09-01'), '%Y-%m-%d') THEN CASE WHEN STR_TO_DATE(CONCAT(students.bachelors_start_year, '-09-01'), '%Y-%m-%d') <= projects.project_start_date AND
                                                        projects.project_start_date < STR_TO_DATE(CONCAT(students.bachelors_start_year + 1, '-09-01'), '%Y-%m-%d') THEN '1' WHEN STR_TO_DATE(CONCAT(students.bachelors_start_year + 1, '-09-01'), '%Y-%m-%d') <= projects.project_start_date AND
                                                        projects.project_start_date < STR_TO_DATE(CONCAT(students.bachelors_start_year + 2, '-09-01'), '%Y-%m-%d') THEN '2' WHEN STR_TO_DATE(CONCAT(students.bachelors_start_year + 2, '-09-01'), '%Y-%m-%d') <= projects.project_start_date AND
                                                        projects.project_start_date < STR_TO_DATE(CONCAT(students.bachelors_start_year + 3, '-09-01'), '%Y-%m-%d') THEN '3' WHEN STR_TO_DATE(CONCAT(students.bachelors_start_year + 3, '-09-01'), '%Y-%m-%d') <= projects.project_start_date AND
                                                        projects.project_start_date < STR_TO_DATE(CONCAT(students.bachelors_start_year + 4, '-09-01'), '%Y-%m-%d') THEN '4' ELSE NULL END ELSE CASE WHEN STR_TO_DATE(CONCAT(students.masters_start_year, '-09-01'), '%Y-%m-%d') <= projects.project_start_date AND
                                                    projects.project_start_date < STR_TO_DATE(CONCAT(students.masters_start_year + 1, '-09-01'), '%Y-%m-%d') THEN '1' WHEN STR_TO_DATE(CONCAT(students.masters_start_year + 1, '-09-01'), '%Y-%m-%d') <= projects.project_start_date AND
                                                    projects.project_start_date < STR_TO_DATE(CONCAT(students.masters_start_year + 2, '-09-01'), '%Y-%m-%d') THEN '2' ELSE NULL END END AS 'Курс в моменте',
                                            CASE WHEN students.masters_start_year = 0 OR
                                                students.masters_start_year IS NULL OR
                                                projects.project_start_date < STR_TO_DATE(CONCAT(students.masters_start_year, '-09-01'), '%Y-%m-%d') THEN 'Бакалавриат' ELSE 'Магистратура' END AS 'Программа в моменте',
                                            CASE WHEN students.masters_start_year = 0 OR
                                                students.masters_start_year IS NULL OR
                                                projects.project_start_date < STR_TO_DATE(CONCAT(students.masters_start_year, '-09-01'), '%Y-%m-%d') THEN Бакалавры.university_name ELSE Магистры.university_name END AS 'ВУЗ в моменте',
                                            CASE
                                                    WHEN YEAR(projects.project_start_date) = 0
                                                        THEN NULL
                                                    WHEN MONTH(projects.project_start_date) > 8
                                                        THEN CONCAT_WS(' - ', YEAR(projects.project_start_date), YEAR(projects.project_start_date)+1)
                                                    ELSE CONCAT_WS(' - ', YEAR(projects.project_start_date)-1, YEAR(projects.project_start_date))
                                                END AS `Академический год`
                                            FROM students_in_projects
                                            LEFT OUTER JOIN projects
                                                ON students_in_projects.project_id = projects.project_id
                                            LEFT OUTER JOIN students
                                                ON students_in_projects.student_id = students.student_id
                                            LEFT OUTER JOIN (SELECT
                                                students.student_id,
                                                universities.university_name,
                                                regions.region
                                                FROM students
                                                INNER JOIN universities
                                                    ON students.bachelors_university_id = universities.university_id
                                                INNER JOIN regions
                                                    ON universities.university_region_id = regions.region_id) Бакалавры
                                                ON students.student_id = Бакалавры.student_id
                                            LEFT OUTER JOIN (SELECT
                                                students.student_id,
                                                universities.university_name,
                                                regions.region
                                                FROM students
                                                INNER JOIN universities
                                                    ON students.masters_university_id = universities.university_id
                                                INNER JOIN regions
                                                    ON universities.university_region_id = regions.region_id) Магистры
                                                ON
                                                  students.student_id = Магистры.student_id;
                                            """,
                "projects_report_query"  :  """
                                            SELECT
                                            students.student_id AS `ID студента`,
                                            CONCAT_WS(
                                                ' ',
                                                students.student_surname,
                                                students.student_name,
                                                students.student_midname)
                                            AS 'ФИО студента',
                                            T0.project_id AS `ID проекта`,
                                            T0.project_name AS `Название проекта`,
                                            T0.company_name AS `Название компании`,
                                            CASE
                                                WHEN T0.is_frozen = 1
                                                THEN 'Заморожен'
                                                WHEN T0.is_frozen <> 1 AND (DAYNAME(T0.project_end_date) IS NULL OR DATE(T0.project_end_date) >= CURDATE())
                                                THEN 'Активен' ELSE 'Завершен'
                                            END AS Статус,
                                            students_in_projects.team AS Команда,
                                            students_in_projects.is_curator AS Куратор,
                                            students_in_projects.is_moderator AS Модератор,
                                            CASE WHEN students.masters_start_year = 0 OR
                                                students.masters_start_year IS NULL OR
                                                T0.project_start_date < STR_TO_DATE(CONCAT(students.masters_start_year, '-09-01'), '%Y-%m-%d') THEN CASE WHEN STR_TO_DATE(CONCAT(students.bachelors_start_year, '-09-01'), '%Y-%m-%d') <= T0.project_start_date AND
                                                        T0.project_start_date < STR_TO_DATE(CONCAT(students.bachelors_start_year + 1, '-09-01'), '%Y-%m-%d') THEN '1' WHEN STR_TO_DATE(CONCAT(students.bachelors_start_year + 1, '-09-01'), '%Y-%m-%d') <= T0.project_start_date AND
                                                        T0.project_start_date < STR_TO_DATE(CONCAT(students.bachelors_start_year + 2, '-09-01'), '%Y-%m-%d') THEN '2' WHEN STR_TO_DATE(CONCAT(students.bachelors_start_year + 2, '-09-01'), '%Y-%m-%d') <= T0.project_start_date AND
                                                        T0.project_start_date < STR_TO_DATE(CONCAT(students.bachelors_start_year + 3, '-09-01'), '%Y-%m-%d') THEN '3' WHEN STR_TO_DATE(CONCAT(students.bachelors_start_year + 3, '-09-01'), '%Y-%m-%d') <= T0.project_start_date AND
                                                        T0.project_start_date < STR_TO_DATE(CONCAT(students.bachelors_start_year + 4, '-09-01'), '%Y-%m-%d') THEN '4' ELSE NULL END ELSE CASE WHEN STR_TO_DATE(CONCAT(students.masters_start_year, '-09-01'), '%Y-%m-%d') <= T0.project_start_date AND
                                                    T0.project_start_date < STR_TO_DATE(CONCAT(students.masters_start_year + 1, '-09-01'), '%Y-%m-%d') THEN '1' WHEN STR_TO_DATE(CONCAT(students.masters_start_year + 1, '-09-01'), '%Y-%m-%d') <= T0.project_start_date AND
                                                    T0.project_start_date < STR_TO_DATE(CONCAT(students.masters_start_year + 2, '-09-01'), '%Y-%m-%d') THEN '2' ELSE NULL END END AS 'Курс',
                                            CASE WHEN students.masters_start_year = 0 OR
                                                students.masters_start_year IS NULL OR
                                                T0.project_start_date < STR_TO_DATE(CONCAT(students.masters_start_year, '-09-01'), '%Y-%m-%d') THEN 'Бакалавриат' ELSE 'Магистратура' END AS 'Программа в моменте',
                                            CASE WHEN students.masters_start_year = 0 OR
                                                students.masters_start_year IS NULL OR
                                                T0.project_start_date < STR_TO_DATE(CONCAT(students.masters_start_year, '-09-01'), '%Y-%m-%d') THEN Бакалавры.university_name ELSE Магистры.university_name END AS 'ВУЗ',
                                            CASE
                                                    WHEN YEAR(T0.project_start_date) = 0
                                                        THEN NULL
                                                    WHEN MONTH(T0.project_start_date) > 8
                                                        THEN CONCAT_WS(' - ', YEAR(T0.project_start_date), YEAR(T0.project_start_date)+1)
                                                    ELSE CONCAT_WS(' - ', YEAR(T0.project_start_date)-1, YEAR(T0.project_start_date))
                                                END AS `Академический год`
                                            FROM students_in_projects
                                            LEFT OUTER JOIN (SELECT
                                                *
                                                FROM projects
                                                    LEFT JOIN companies
                                                        ON projects.project_company_id = companies.company_id) AS T0
                                                ON students_in_projects.project_id = T0.project_id
                                            LEFT OUTER JOIN students
                                                ON students_in_projects.student_id = students.student_id
                                            LEFT OUTER JOIN (SELECT
                                                students.student_id,
                                                universities.university_name,
                                                regions.region
                                                FROM students
                                                INNER JOIN universities
                                                    ON students.bachelors_university_id = universities.university_id
                                                INNER JOIN regions
                                                    ON universities.university_region_id = regions.region_id) Бакалавры
                                                ON students.student_id = Бакалавры.student_id
                                            LEFT OUTER JOIN (SELECT
                                                students.student_id,
                                                universities.university_name,
                                                regions.region
                                                FROM students
                                                INNER JOIN universities
                                                    ON students.masters_university_id = universities.university_id
                                                INNER JOIN regions
                                                    ON universities.university_region_id = regions.region_id) Магистры
                                                ON students.student_id = Магистры.student_id;
                                            """,

                "universities_in_projects": """
                                            SELECT DISTINCT
                                            students_in_projects.project_id  AS `ID проекта`,
                                            universities.university_id  AS `ID университета`,
                                            universities.university_name  AS `Университет`
                                            FROM students_in_projects
                                            INNER JOIN students
                                                ON students_in_projects.student_id = students.student_id
                                            INNER JOIN universities
                                                ON students.bachelors_university_id = universities.university_id;
                                            """,

                "universities_in_events":   """
                                            SELECT DISTINCT
                                            participants_in_events.event_id  AS `ID мероприятия`,
                                            universities.university_id  AS `ID университета`,
                                            universities.university_name  AS `Университет`
                                            FROM participants_in_events
                                            INNER JOIN students
                                                ON participants_in_events.student_id = students.student_id
                                            INNER JOIN universities
                                                ON students.bachelors_university_id = universities.university_id;
                                            """
                
}