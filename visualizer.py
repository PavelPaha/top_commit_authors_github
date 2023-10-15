import asyncio

from manim import *
from git_hunter import GitHunterAsync


class Visualize(Scene):

    def fit_to_frame(self, mobject):
        frame_dimensions = config.frame_width, config.frame_height
        object_dimensions = mobject.width, mobject.height
        scale_ratio = min(frame_dim / object_dim for frame_dim, object_dim in zip(frame_dimensions, object_dimensions))
        mobject.scale(scale_ratio)


    def construct(self):
        hunter = GitHunterAsync('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', 'naumen')

        statistic = asyncio.run(hunter.gather_data())

        label_list, data = zip(*statistic[:5])
        chart = BarChart(data, bar_names=label_list)
        for label in chart.x_axis.labels:
            label.rotate(-PI / 4)

        self.play(GrowFromCenter(chart))
        self.wait(1)
        self.play(FadeOut(chart, target_position=DOWN))

        self.wait(1)
        repo_diagrams = []

        repos_statistic = hunter.repos_statistic

        repos_for_table = repos_statistic[:6]
        for repo_data in repos_for_table:
            repo_name, st = repo_data
            st = st.most_common()
            print(f"REPODATA = {repo_name}, {st}")
            label_list, data = zip(*st)
            chart = BarChart(data, bar_names=label_list)
            for label in chart.x_axis.labels:
                # label.rotate(-PI / 4)
                label.shift(0.5 * (DOWN + RIGHT))

            repo_diagrams += [chart]

        table = VGroup(
            VGroup(repo_diagrams[0], repo_diagrams[1]).arrange(DOWN, buff=0.3),
            VGroup(repo_diagrams[2], repo_diagrams[3]).arrange(DOWN, buff=0.3),
            VGroup(repo_diagrams[4], repo_diagrams[5]).arrange(DOWN, buff=0.3)
        ).arrange(RIGHT, buff=0.5)
        self.fit_to_frame(table)

        self.play(Write(table))
        self.wait()
        self.play(FadeOut(table))
