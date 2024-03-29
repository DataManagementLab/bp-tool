from bp.templatetags.tags_project_overview_list import ProjectOverviewColumnTags

grade_column = ProjectOverviewColumnTags(priority=7 * 128)


@grade_column.register_description('bp/grading/orga/project_overview_list_column_grade_desc.html')
def grade_column_description(**kwargs):
    return {}


@grade_column.register_content('bp/grading/orga/project_overview_list_column_grade_content.html')
def grade_column_content(project, **kwargs):
    return {'pitch': project.pitch_grade_points,
            'ag': project.ag_grade_points,
            'docs': project.docs_grade_points,
            'total': project.total_points,
            'grade': project.grade if project.grade_complete else 0,
            'div_id': f"div_{project.pk}",
            'grade_is_close_to_higher_grade': project.grade_close_to_higher_grade,
            }
