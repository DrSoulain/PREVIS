import os

from matplotlib import pyplot as plt

import previs


def perform_search(args):
    d = previs.search(args.target, check=args.check, verbose=args.verbose)

    if args.save_to is not None:
        if not os.path.exists(args.save_to):
            os.mkdir(args.save_to)

    previs.plot_VLTI(d)
    if args.save_to is not None:
        filefig = os.path.join(args.save_to, f"{args.target}_VLTI.pdf")
        plt.savefig(filefig)

    previs.plot_CHARA(d)
    if args.save_to is not None:
        filefig = os.path.join(args.save_to, f"{args.target}_CHARA.pdf")
        plt.savefig(filefig)

    if args.plot:
        plt.show()

    if args.save_to is not None:
        result_file = os.path.join(args.save_to, f"{args.target}.json")
        previs.save(d, result_file=result_file, overwrite=True)
    return 0


def perform_survey(args):
    survey = previs.survey(args.target)

    if args.save_to is not None:
        if not os.path.exists(args.save_to):
            os.mkdir(args.save_to)

    if args.save_to is not None:
        result_file = os.path.join(args.save_to, "survey.json")
        previs.save(survey, result_file=result_file, overwrite=True)

    count_survey = previs.count_survey(survey)

    previs.plot_histo_survey(count_survey, plot_HR=True)
    if args.plot:
        plt.show()
    return 0
