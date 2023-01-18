query_dict =    {
                "projects"              :   """
                                            SELECT
                                                projects.project_id AS 'ID проекта',
                                                T1.company_id AS 'ID компании',
                                                T1.company_name AS 'Название компании',
                                                T2.company_type AS 'Тип компании',
                                                T3.company_sphere AS 'Отрасль',
                                                projects.project_name AS 'Название проекта',
                                                projects.project_description AS 'Описание',
                                                projects.project_result AS 'Результат',
                                                projects.project_start_date AS 'Дата начала',
                                                projects.project_end_date AS 'Дата окончания',
                                                project_grades.grade AS 'Грейд',
                                                T00.sphere AS 'Макро-направление',
                                                T0.field AS 'Микро-направление',
                                                CASE
                                                    WHEN
                                                        projects.is_frozen = 1
                                                    THEN 'Заморожен'
                                                    WHEN
                                                        projects.is_frozen != 1 AND (DAYNAME(projects.project_end_date) IS NULL OR DATE(projects.project_end_date) >= CURDATE())
                                                    THEN 'Активен' 
                                                    ELSE 'Завершен'
                                                END AS 'Статус'
                                            FROM projects 
                                            LEFT JOIN project_grades
                                                ON projects.project_grade_id   = project_grades.grade_id
                                            LEFT JOIN   (
                                                            (SELECT project_fields.field_id, project_fields.field, project_fields.sphere_id FROM project_fields) AS T0
                                                                LEFT JOIN
                                                                    (SELECT field_spheres.sphere_id, field_spheres.sphere FROM field_spheres) AS T00
                                                                ON T0.sphere_id = T00.sphere_id
                                                        )
                                                ON projects.project_field_id = T0.field_id
                                            LEFT JOIN   (
                                                            (SELECT companies.company_id, companies.company_name, companies.company_type_id, companies.company_sphere_id FROM companies) AS T1
                                                                LEFT JOIN 
                                                                    (SELECT company_types.company_type_id, company_types.company_type FROM company_types) AS T2
                                                                    ON T1.company_type_id = T2.company_type_id
                                                                LEFT JOIN
                                                                    (SELECT company_spheres.company_sphere_id, company_spheres.company_sphere FROM company_spheres) AS T3
                                                                    ON T1.company_sphere_id = T3.company_sphere_id
                                                        )
                                                ON projects.project_company_id = T1.company_id;
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
                                                    WHEN students.student_id in (SELECT managers_in_projects.student_id FROM managers_in_projects)
                                                    THEN 1
                                                    ELSE 0
                                                END AS 'Опыт менеджера',
                                                CASE
                                                    WHEN students.student_id in (SELECT students_in_projects.student_id FROM students_in_projects WHERE students_in_projects.is_curator = 1)
                                                    THEN 1
                                                    ELSE 0
                                                END AS 'Опыт куратора',
                                                bach_name AS 'Бакалавриат',
                                                bach_reg_name AS 'Бак. регион',
                                                students.bachelors_start_year AS 'Бак. год',
                                                mast_name AS 'Магистратура',
                                                mast_reg_name as 'Маг. регион',
                                                students.masters_start_year AS 'Маг. год',
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
                                            universities.university_name AS 'Название',
                                            T0.region AS 'Регион'
                                            FROM universities
                                            LEFT JOIN   (SELECT regions.region_id, regions.region FROM regions) AS T0
                                                ON universities.university_id = T0.region_id;
                                            """,

                "students_in_projects"  :   """
                                            SELECT
                                                students_in_projects.project_id AS 'ID проекта',
                                                students_in_projects.student_id AS 'ID студента',
                                                CASE
                                                    WHEN
                                                        T1.is_frozen = 1
                                                    THEN 'Заморожен'
                                                    WHEN
                                                        T1.is_frozen != 1 AND (DAYNAME(T1.project_end_date) IS NULL OR DATE(T1.project_end_date) >= CURDATE())
                                                    THEN 'Активен' 
                                                    ELSE 'Завершен'
                                                END AS 'Статус',
                                                students_in_projects.team AS 'Команда',
                                                students_in_projects.is_curator AS 'Куратор'
                                            FROM students_in_projects
                                            LEFT JOIN   (
                                                            SELECT 
                                                                projects.project_id,
                                                                projects.is_frozen,
                                                                projects.project_end_date
                                                            FROM projects 
                                                        ) AS T1
                                                ON students_in_projects.project_id = T1.project_id;
                                            """,
                "managers_in_projects"  :   """
                                            SELECT
                                                managers_in_projects.project_id AS 'ID проекта',
                                                managers_in_projects.student_id AS 'ID студента'
                                            FROM managers_in_projects;
                                            """,

                "teachers_in_projects"  :   """
                                            SELECT
                                                teachers_in_projects.project_id AS 'ID проекта',
                                                teachers_in_projects.teacher_id AS 'ID преподавателя'
                                            FROM teachers_in_projects;
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
}